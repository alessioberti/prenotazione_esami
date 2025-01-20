from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, JWTManager, decode_token
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session 
from datetime import date, datetime, time, timedelta
import logging, traceback
from werkzeug.security import check_password_hash, generate_password_hash
import re
from flask_cors import CORS
from database import engine, OperatorsAvailability, Operator, Laboratory, SlotBooking, LaboratoryClosure, OperatorAbsence, ExamType, Account
from operators_availability import generate_availabile_slots

#https://flask.palletsprojects.com/en/stable/quickstart/
#https://flask-login.readthedocs.io/en/latest/
#https://flask-jwt-extended.readthedocs.io/en/stable/

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "supersegreto123"
jwt = JWTManager(app)
logging.basicConfig(level=logging.INFO)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
BLOCKLIST = set()

@app.post("/register")
def register():
    new_account = request.json
    if not new_account:
        return jsonify({"Request invalid":"missing JSON body"}), 400

    #username_regex = r'^[0-9A-Za-z]{6,16}$'
    password_regex = r'^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}$'
    email_regex    = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    tel_number_regex = r'^\+?\d{10,13}$'

    #if not re.match(username_regex, new_account.get("username")):
    #    return jsonify({"error": "Invalid username"}), 400
    if not re.match(password_regex, new_account.get("password")):
        return jsonify({"error": "Invalid password"}), 400
    if not re.match(email_regex, new_account.get("email")):
        return jsonify({"error": "Invalid email"}), 400
    #if not re.match(tel_number_regex, new_account.get("tel_number")):
       # return jsonify({"error": "Invalid tel_number"}), 400
    
    new_account = Account(
        username=new_account.get("username"),
        password_hash = generate_password_hash(new_account.get("password")),
        email=new_account.get("email"),
        tel_number=new_account.get("tel_number")
    )

    with Session(engine) as session:
        session.add(new_account)
        try:
            session.commit()
            session.refresh(new_account)
        except IntegrityError:
            session.rollback()
            return jsonify({"error": "Integrity Error"}), 400

    return jsonify({"message": "Account created"}), 200

@app.post("/login")
def login():
    account_data = request.json
    if not account_data:
        return jsonify({"error":"missing JSON body"}), 400
    
    with Session(engine) as session:
        account_query = select(Account).where(Account.username == account_data.get("username"))
        account = session.execute(account_query).scalars().first()

        if not account:
            return jsonify({"error": "Invalid username or password"}), 401
        
        if not account.enabled:
            return jsonify({"error": "Account disabled"}), 403

        if (account.failed_login_count >= 5) and ((datetime.now() - account.last_failed_login) < timedelta(minutes=5)):
            return jsonify({"error": "Too many login attempts"}), 401

        if  check_password_hash(account.password_hash, account_data.get("password")):
        
            account.failed_login_count = 0
            account.last_failed_login = None
            session.commit()

            access_token = create_access_token(identity=account.account_id)
            return jsonify(access_token=access_token), 200
        
        else:
            account.failed_login_count = account.failed_login_count + 1
            account.last_failed_login = datetime.now()
            session.commit()

            return jsonify({"error": "Invalid username or password"}), 401
            
@app.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)
    return jsonify({"Success": "Logged out"}), 200

@app.get('/slots_availability')
@jwt_required()
def get_slots_availability():
   
    datetime_from_filter = request.args.get('datetime_from_filter')
    datetime_to_filter = request.args.get('datetime_to_filter'),
    exam_type_id = request.args.get('exam_type_id', type=int)
    operator_id = request.args.get('operator_id', type=int)
    laboratory_id = request.args.get('laboratory_id', type=int)

    # Imposta un controllo sulla data di partenza della verifica delle disponibilità che non può essere nel passato o nel giorno corrente
    first_reservation_datetime = datetime.combine(datetime.now(() + timedelta(days=1)).date(), time(0, 0))
    
    # Se viene richiesta una data superiore può essere inserita quella 

    if datetime_from_filter:
        try:
            datetime_from_filter = max((datetime.strptime(datetime_from_filter, '%Y-%m-%d %H:%M:%S')), first_reservation_datetime)
        except ValueError:
            return jsonify({"error": "Invalid from datetime format. Use YYYY-MM-DD HH:MM:SS"}), 400
    else:
        datetime_from_filter = first_reservation_datetime

    # Immposta un controllo sulla data massima di generazione degli slot a 60 giorni dalla data odierna
    last_reservation_datetime = datetime.combine(datetime.now(() + timedelta(days=60)).date(), time(0, 0))

    # se viene inserita una data infeririore può essere inserita quella

    if datetime_from_filter:
        try:
            datetime_to_filter = min((datetime.strptime(datetime_from_filter, '%Y-%m-%d %H:%M:%S')), last_reservation_datetime)
        except ValueError:
            return jsonify({"error": "Invalid from datetime format. Use YYYY-MM-DD HH:MM:SS"}), 400
    else:
        datetime_to_filter = last_reservation_datetime

    logging.info("data inizio generazione slot: %s", datetime_from_filter)
    logging.info("data fine generazione slot: %s", datetime_to_filter)

    # tramite la sessione crea la availability_query
    with Session(engine) as session:

        # Crea la query per gli slot prenotabili
        logging.info("Esecuzione Query")
        logging.info(
        "Parametri: exam_type_id=%s, operator_id=%s, laboratory_id=%s, datetime_from_filter=%s",
             exam_type_id, operator_id, laboratory_id, datetime_from_filter
        )

        # Query per gli slot già prenotati

        booked_slots_query = (
            select(SlotBooking)
            .join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id)
            .where(SlotBooking.rejected == False)
        )

        if datetime_from_filter:
            booked_slots_query = booked_slots_query.where(SlotBooking.appointment_date >= datetime_from_filter.date())
        if exam_type_id:
            booked_slots_query = booked_slots_query.where(OperatorsAvailability.exam_type_id == exam_type_id)
        if operator_id:
            booked_slots_query = booked_slots_query.where(OperatorsAvailability.operator_id == operator_id)
        if laboratory_id:
            booked_slots_query = booked_slots_query.where(OperatorsAvailability.laboratory_id == laboratory_id)

        booked_slots = session.execute(booked_slots_query).scalars().all()

        # Crea la query per i periodi di chiusura dei laboratori
        laboratory_closures_query = select(LaboratoryClosure)
        
        if datetime_from_filter:
            laboratory_closures_query = laboratory_closures_query.where(LaboratoryClosure.end_datetime >= datetime_from_filter)
        if laboratory_id:
            laboratory_closures_query = laboratory_closures_query.where(LaboratoryClosure.laboratory_id == laboratory_id)

        laboratory_closures = session.execute(laboratory_closures_query).scalars().all()

        # Crea la query per i periodi di assenza degli operatori
        operator_absences_query  = select(OperatorAbsence)

        if datetime_from_filter:
            operator_absences_query = operator_absences_query.where(OperatorAbsence.end_datetime >= datetime_from_filter)
        if operator_id:
            operator_absences_query = operator_absences_query.where(OperatorAbsence.operator_id == operator_id)

        operator_absences = session.execute(operator_absences_query).scalars().all()
        
        availability_query = (
            select(OperatorsAvailability)
            .join(Operator, OperatorsAvailability.operator_id == Operator.operator_id)
            .join(Laboratory, OperatorsAvailability.laboratory_id == Laboratory.laboratory_id)
            .join(ExamType, OperatorsAvailability.exam_type_id == ExamType.exam_type_id)
            .where(OperatorsAvailability.enabled == True)
        )

        if datetime_from_filter:
            availability_query = availability_query.where(OperatorsAvailability.available_to_date >= datetime_from_filter.date())
        if exam_type_id:
            availability_query = availability_query.where(OperatorsAvailability.exam_type_id == exam_type_id)
        if operator_id:
            availability_query = availability_query.where(OperatorsAvailability.operator_id == operator_id)
        if laboratory_id:
            availability_query = availability_query.where(OperatorsAvailability.laboratory_id == laboratory_id)

        availability = session.execute(availability_query).scalars().all()

        try:
            slots = generate_availabile_slots(availability, datetime_from_filter, laboratory_closures, operator_absences, booked_slots)
            logging.info("Slots generated: %s", len(slots))
            return jsonify(slots), 200
        except Exception as e:
            logging.error("Error in slot conversion:\n%s", traceback.format_exc())
            return jsonify({"error": "Slot conversion Error"}), 500

@app.get("/operators")
@jwt_required()
def get_operators():

    exam_id = request.args.get("exam_id")
    laboratory_id = request.args.get("laboratory_id")

    with Session(engine) as session:
        
        operators_query = select(Operator).join(OperatorsAvailability, OperatorsAvailability.operator_id == Operator.operator_id).distinct()

        if exam_id:
            operators_query = operators_query.where(OperatorsAvailability.exam_type_id == exam_id)
        if laboratory_id:
            operators_query = operators_query.where(OperatorsAvailability.laboratory_id == laboratory_id)  

        operators = session.execute(operators_query).scalars().all()

        operators_list = []
        for operator in operators:
            operators_list.append({
                "operator_id": operator.operator_id,
                "name": operator.name
            })

    return jsonify(operators_list), 200

@app.get("/exam_types")
@jwt_required()
def get_exam_types():

    current_user = get_jwt_identity()  # Ottieni l'utente corrente dal token
    logging.error(f"Richiesta ricevuta da utente: {current_user}")
    with Session(engine) as session:

        exam_types_query = select(ExamType)
        exam_types = session.execute(exam_types_query).scalars().all()

        exam_types_list = []
        for et in exam_types:
            exam_types_list.append({
                "exam_type_id": et.exam_type_id,
                "name": et.name,
                "description": et.description
            })

    return jsonify(exam_types_list), 200

@app.get("/laboratories")
@jwt_required()
def get_laboratories():

    exam_id = request.args.get("exam_id")
    operator_id = request.args.get("operator_id")

    with Session(engine) as session:
        
        laboratories_query = select(Laboratory).join(OperatorsAvailability, Laboratory.laboratory_id == OperatorsAvailability.laboratory_id).distinct()

        if exam_id:
            laboratories_query = laboratories_query.where(OperatorsAvailability.exam_type_id == exam_id)
        if operator_id:
            laboratories_query = laboratories_query.where(OperatorsAvailability.operator_id == operator_id)  

        laboratories = session.execute(laboratories_query).scalars().all()

        labs_list = []
        for lab in laboratories:
            labs_list.append({
                "laboratory_id": lab.laboratory_id,
                "name": lab.name,
                "address": lab.address,
                "contact_info": lab.contact_info
            })

    return jsonify(labs_list), 200

@app.post("/book_slot")
@jwt_required()
def book_slot():

    slot = request.json
    current_user = get_jwt_identity()

    if not slot:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        appointment_time_start = time.fromisoformat(slot["operator_availability_slot_start"])
        appointment_time_end  =time.fromisoformat(slot["operator_availability_slot_end"])
        appointment_date = date.fromisoformat(slot["operator_availability_date"])
        
    except (KeyError, ValueError):
        return jsonify({"error": "Missing key or invalid value format"}), 400

    with Session(engine) as session:

        new_booking = SlotBooking(
            account_id=current_user,
            availability_id=slot.get("availability_id"),
            appointment_time_start = appointment_time_start,
            appointment_datetime_end = appointment_time_end,
            appointment_date = appointment_date,
            rejected=slot.get("rejected", False)
        )

        try:
            session.add(new_booking)
            session.commit()
        except IntegrityError:
            session.rollback()
            return jsonify({"error": "Integrity Error"})
        return jsonify({"message": "Booking Complete"}), 200
         
@app.get("/slot_bookings")
@jwt_required()
def get_booked_slots():

    current_user = get_jwt_identity()

    with Session(engine) as session:

        booked_slots_query = select(SlotBooking).where(SlotBooking.account_id == current_user)
        booked_slots = session.execute(booked_slots_query).scalars().all()

        slots_list = []
        for slot in booked_slots:
            slots_list.append({
                "slot_id": slot.slot_id,
                "availability_id": slot.availability_id,
                "appointment_date": slot.appointment_date.isoformat(),
                "appointment_time_start": slot.appointment_time_start.isoformat(),
                "appointment_time_end": slot.appointment_time_end.isoformat(),
                "rejected": slot.rejected
            })

    return jsonify(slots_list), 200

@app.delete("/book_slot/<int:slot_id>")
@jwt_required()
def delete_booked_slot(slot_id):

    current_user = get_jwt_identity()
    
    with Session(engine) as session:
        slot_query = select(SlotBooking).where(SlotBooking.slot_id == slot_id)
        slot = session.execute(slot_query).scalars().first()

        if not slot:
            return jsonify({"error": "Slot not found"}), 404
        
        if not slot.account_id == current_user:
            return jsonify({"error": "Unauthorized"}), 401

        session.delete(slot)
        session.commit()

        return jsonify({"Success": "Slot deleted"}), 200
    


