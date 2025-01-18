from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session 
from datetime import date, datetime, time, timedelta
from database import engine, OperatorsAvailability, Operator, Laboratory, SlotBooking, LaboratoryClosure, OperatorAbsence, ExamType, Account
import logging, traceback
from operators_availability import generate_availabile_slots
from werkzeug.security import check_password_hash, generate_password_hash
import re

#https://flask.palletsprojects.com/en/stable/quickstart/
#https://flask-login.readthedocs.io/en/latest/

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersegreto123"
logging.basicConfig(level=logging.INFO)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):

    with Session(engine) as session:
        
        account_query= select(Account).where(Account.account_id == user_id)
        account_query = session.execute(account_query)

        return account_query.scalars().first()

@app.post("/register")
def register():
    new_account = request.json
    if not new_account:
        return jsonify({"Request invalid":"missing JSON body"}), 400

    username_regex = r'^[0-9A-Za-z]{6,16}$'
    password_regex = r'^(?=.*?[0-9])(?=.*?[A-Za-z]).{8,32}$'
    email_regex    = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    tel_number_regex = r'^\+?\d{10,13}$'


    if not re.match(username_regex, new_account.get("username")):
        return jsonify({"error": "Invalid username"}), 400
    if not re.match(password_regex, new_account.get("password")):
        return jsonify({"error": "Invalid password"}), 400
    if not re.match(email_regex, new_account.get("email")):
        return jsonify({"error": "Invalid email"}), 400
    if not re.match(tel_number_regex, new_account.get("tel_number")):
        return jsonify({"error": "Invalid tel_number"}), 400
    
    pw_hash = generate_password_hash(new_account.get("password"))

    new_account = Account(
        username=new_account.get("username"),
        password_hash=pw_hash,
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

        if (account.last_failed_login > 5) and ((datetime.now() - account.last_failed_login) < timedelta(minutes=5)):
            return jsonify({"error": "Too many login attempts"}), 401

        if not account or (not check_password_hash(account.password_hash, account_data.get("password"))):
            return jsonify({"error": "Invalid username or password"}), 401
        
        login_user(account)
        return jsonify({"message": "Logged in"}), 200

@app.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"Success": "Logged out"}), 200

@app.get('/slots_availability')
@login_required
def get_slots_availability():
   
    datetime_from_filter = request.args.get('datetime_from_filter')
    exam_type_id = request.args.get('exam_type_id', type=int)
    operator_id = request.args.get('operator_id', type=int)
    laboratory_id = request.args.get('laboratory_id', type=int)

    # Imposta un controllo sulla data di partenza della verifica delle disponibilità che non può essere nel passato o nel giorno corrente
    # può essere richiesta la disponibità dalla data successiva alla data odierna
    first_reservation_datetime = datetime.combine((datetime.now('Europe/Rome') + timedelta(days=1)).date(), time(0, 0))
    if datetime_from_filter:
        try:
            datetime_from_filter = max((datetime.strptime(datetime_from_filter, '%Y-%m-%d %H:%M:%S')), first_reservation_datetime)
        except ValueError:
            return jsonify({"error": "Invalid datetime format. Use YYYY-MM-DD HH:MM:SS"}), 400
    else:
        datetime_from_filter = first_reservation_datetime

    logging.info("datetime_from_filter calcolato: %s", datetime_from_filter)

    # tramite la sessione crea la availability_query
    with Session(engine) as session:

        # Crea la query per gli slot prenotabili
        logging.info("Esecuzione Query")
        logging.info(
        "Parametri: exam_type_id=%s, operator_id=%s, laboratory_id=%s, datetime_from_filter=%s",
             exam_type_id, operator_id, laboratory_id, datetime_from_filter
        )

        booked_slots_query = (
            select(SlotBooking)
            .join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id)
            .where(SlotBooking.rejected == False)
        )

        if datetime_from_filter:
            booked_slots_query = booked_slots_query.where(SlotBooking.appointment_datetime_end >= datetime_from_filter)
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
@login_required
def get_operators():

    operator_id = request.args.get("operator_id", type=int)

    with Session(engine) as session:
        
        operators_query = select(Operator)
        if operator_id:
            operators_query = operators_query.where(Operator.operator_id == operator_id)

        operators= session.execute(operators_query).scalars().all()

        operators_list = []
        for operator in operators:
            operators_list.append({
                "operator_id": operator.operator_id,
                "name": operator.name
            })

    return jsonify(operators_list), 200

@app.get("/exam_types")
@login_required
def get_exam_types():
    exam_type_id = request.args.get("exam_type_id", type=int)

    with Session(engine) as session:

        exam_types_query = select(ExamType)
        if exam_type_id:
            exam_types_query = exam_types_query.where(ExamType.exam_type_id == exam_type_id)

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
@login_required
def get_laboratories():
    laboratory_id = request.args.get("laboratory_id", type=int)

    with Session(engine) as session:

        laboratories_query = select(Laboratory)
        if laboratory_id:
            laboratories_query = laboratories_query.where(Laboratory.laboratory_id == laboratory_id)

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
@login_required
def book_slot():

    slot = request.json

    if not slot:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        operator_availability_slot_start=time.fromisoformat(slot["operator_availability_slot_start"])
        operator_availability_slot_end=time.fromisoformat(slot["operator_availability_slot_end"])
        operator_availability_date=date.fromisoformat(slot["operator_availability_date"])
        appointment_datetime_start = datetime.combine(operator_availability_date, operator_availability_slot_start)
        appointment_datetime_end = datetime.combine(operator_availability_date, operator_availability_slot_end)
    except KeyError or ValueError:
        return jsonify({"error": "key messing or Vaule Format"}), 400

    with Session(engine) as session:

        new_booking = SlotBooking(
            account_id=current_user.account_id,
            availability_id=slot.get("availability_id"),
            appointment_datetime_start = appointment_datetime_start,
            appointment_datetime_end = appointment_datetime_end,
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
@login_required
def get_booked_slots():

    with Session(engine) as session:

        booked_slots_query = select(SlotBooking).where(SlotBooking.account_id == current_user.account_id)
        booked_slots = session.execute(booked_slots_query).scalars().all()

        slots_list = []
        for slot in booked_slots:
            slots_list.append({
                "slot_id": slot.slot_id,
                "availability_id": slot.availability_id,
                "appointment_datetime_start": slot.appointment_datetime_start.isoformat(),
                "appointment_datetime_end": slot.appointment_datetime_end.isoformat(),
                "rejected": slot.rejected
            })

    return jsonify(slots_list), 200

@app.delete("/book_slot/<int:slot_id>")
@login_required
def delete_booked_slot(slot_id):

    logged_user = current_user.account_id
    
    with Session(engine) as session:
        slot_query = select(SlotBooking).where(SlotBooking.slot_id == slot_id)
        slot = session.execute(slot_query).scalars().first()

        if not slot:
            return jsonify({"error": "Slot not found"}), 404
        
        if not slot.account_id == logged_user:
            return jsonify({"error": "Unauthorized"}), 401

        session.delete(slot)
        session.commit()

        return jsonify({"Success": "Slot deleted"}), 200
    


