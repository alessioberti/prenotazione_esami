import os
from uuid import UUID
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, JWTManager, set_access_cookies
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session 
from datetime import date, datetime, time, timedelta
import logging, traceback
from werkzeug.security import check_password_hash, generate_password_hash
import re
from flask_cors import CORS
from database import engine, OperatorsAvailability, Operator, Laboratory, SlotBooking, LaboratoryClosure, OperatorAbsence, ExamType, Account
from generate_availabile_slots import generate_availabile_slots
from dotenv import load_dotenv

#https://flask.palletsprojects.com/en/stable/quickstart/
#https://flask-login.readthedocs.io/en/latest/
#https://flask-jwt-extended.readthedocs.io/en/stable/

load_dotenv()
## variabili di configurazione per la sicurezza dei cookie

JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE")
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
CSFR_SECRET_KEY = os.getenv("CSFR_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")
BACKEND_URL = os.getenv("BACKEND_URL")
MAX_BOOKINGS_PER_USER = int(os.getenv("MAX_BOOKINGS_PER_USER", 5))
MAX_DAYS_BOOK_FORWARD = int(os.getenv("MAX_DAYS_BOOK_FORWARD", 60))

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = JWT_COOKIE_SECURE
app.config['JWT_COOKIE_SAMESITE'] = JWT_COOKIE_SAMESITE
jwt = JWTManager(app)

"""
from flask_wtf.csrf import CSRFProtect, generate_csrf
app.config["SECRET_KEY"] = CSFR_SECRET_KEY
#app.config["WTF_CSRF_ALLOWED_ORIGINS"] = [FRONTEND_URL]
app.config["WTF_CSRF_CHECK_REFERRER"] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
csrf = CSRFProtect(app)

@app.before_request
def debug_request():
    csrf_header = request.headers.get("X-CSRF-TOKEN")
    csrf_cookie = request.cookies.get("csrf_access_token")
    #logging.info(f"CSRF Token from Header: {csrf_header}")
    #logging.info(f"CSRF Token from Cookie: {csrf_cookie}")
    if csrf_header != csrf_cookie:
        logging.error("CSRF Token mismatch!")

@app.after_request
def set_csrf_cookie(response):
    csrf_token = generate_csrf()
    response.set_cookie(
        'csrf_access_token',
        csrf_token,
        httponly=False,
        secure=JWT_COOKIE_SECURE,
        samesite=JWT_COOKIE_SAMESITE,
    )
    return response

"""

logging.basicConfig(level=logging.INFO)
CORS(
  app,
  resources={r"/*": {"origins": FRONTEND_URL}},
  supports_credentials=True
)

# Block list per i token JWT invalidi (/logout)
BLOCKLIST = set()
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    is_blocked = jti in BLOCKLIST
    if is_blocked:
        logging.info(f"Token {jti} in blocklist")

    return is_blocked

def get_availability_query(session: Session, filters: dict = None):
    filters = filters or {}
    query = (
        select(OperatorsAvailability)
        .join(Operator, OperatorsAvailability.operator_id == Operator.operator_id)
        .join(Laboratory, OperatorsAvailability.laboratory_id == Laboratory.laboratory_id)
        .join(ExamType, OperatorsAvailability.exam_type_id == ExamType.exam_type_id)
        .where(OperatorsAvailability.enabled == True)
    )

    # Applica filtri opzionali
    if filters.get("exam_id"):
        query = query.where(OperatorsAvailability.exam_type_id == filters["exam_id"])
    if filters.get("operator_id"):
        query = query.where(OperatorsAvailability.operator_id == filters["operator_id"])
    if filters.get("laboratory_id"):
        query = query.where(OperatorsAvailability.laboratory_id == filters["laboratory_id"])
    if filters.get("datetime_from"):
        query = query.where(OperatorsAvailability.available_to_date >= filters["datetime_from"].date())
    if filters.get("datetime_to"):
        query = query.where(OperatorsAvailability.available_from_date <= filters["datetime_to"].date())

    return query


@app.post("/register")
def register():
 
    new_account = request.json
    if not new_account:
        return jsonify({"Request invalid":"missing JSON body"}), 400

    #Almeno una lettera maiuscola, una minuscola, un numero e un simbolo lunghezza da 8 a 32 caratteri
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,32}$'
    #Email valida
    email_regex    = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    #Numero di telefono internazionale
    tel_number_regex = r'^\+?\d{10,13}$'

    if not re.match(password_regex, new_account.get("password", "")):
        return jsonify({"error": "Invalid password"}), 400
    if not re.match(email_regex, new_account.get("email", "")):
        return jsonify({"error": "Invalid email"}), 400
    if not re.match(tel_number_regex, new_account.get("tel_number", "")):
        return jsonify({"error": "Invalid tel_number"}), 400
    
    new_account = Account(
        password_hash = generate_password_hash(new_account.get("password")),
        email=new_account.get("email"),
        tel_number=new_account.get("tel_number"),
        first_name=new_account.get("first_name"),
        last_name=new_account.get("last_name")
    )

    with Session(engine) as session:
        
        email_query = select(Account).where(Account.email == new_account.email)
        if session.execute(email_query).scalars().first():
            return jsonify({"error": "Email already in use"}), 409
        
        session.add(new_account)
        try:
            session.commit()
            session.refresh(new_account)
        except IntegrityError as e:
            session.rollback()
            logging.error("Database Error: %s\n%s", str(e), traceback.format_exc())
            return jsonify({"error": "Integrity Error"}), 400

    return jsonify({"message": "Account created"}), 200

@app.post("/login")
def login():
    account_data = request.json
    
    if not account_data or not account_data.get("email") or not account_data.get("password"):
        return jsonify({"error": "Missing email or password"}), 400
    
    with Session(engine) as session:
        
        account_query = select(Account).where(Account.email == account_data["email"])
        account = session.execute(account_query).scalars().first()
        if not account:
            return jsonify({"error": "Invalid email or password"}), 401
        
        
        if not account.enabled:
            return jsonify({"error": "Account disabled"}), 403
        
        # Controlla se ci sono troppi tentativi di accesso falliti
        if (account.failed_login_count >= 5) and ((datetime.now() - account.last_failed_login) < timedelta(minutes=5)):
            return jsonify({"error": "Too many login attempts"}), 401
       
        if check_password_hash(account.password_hash, account_data["password"]):
            
            # Reset tentativi falliti e aggiorna il database
            account.failed_login_count = 0
            account.last_failed_login = None
            session.commit()

            # Genera il token JWT
            access_token = create_access_token(identity=account.account_id)
            resp = make_response({"message": "Logged in"})
            set_access_cookies(resp, access_token)
            return resp
        
        else:
            # in caso di password errata incrementa i tentativi falliti
            account.failed_login_count += 1
            account.last_failed_login = datetime.now()
            session.commit()
            return jsonify({"error": "Invalid email or password"}), 401

@app.get("/mylogin")
@jwt_required()
def mylogin():

    current_user = UUID(get_jwt_identity())
    with Session(engine) as session:

        account_query = select(Account).where(Account.account_id == current_user)
        account = session.execute(account_query).scalars().first()

        if not account:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "email": account.email,
            "tel_number": account.tel_number,
            "first_name": account.first_name,
            "last_name": account.last_name
        }), 200

@app.post("/logout")
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        logging.info(f"Token {jti} aggiunto alla blocklist con successo")
        return jsonify({"Success": "Logged out"}), 200
    except Exception as e:
        logging.error(f"Errore durante il logout: {e}")
        return jsonify({"error": "Errore durante il logout"}), 500

@app.get("/exam_types")
@jwt_required()
def get_exam_types():
    with Session(engine) as session:
        
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))

        exam_types_query = select(ExamType).offset(offset).limit(limit)
        exam_types = session.execute(exam_types_query).scalars().all()

        exam_types_list = []
        for exam_type in exam_types:
            exam_types_list.append({
                "exam_type_id": str(exam_type.exam_type_id),
                "name": exam_type.name,
                "description": exam_type.description
            })

    return jsonify(exam_types_list), 200

@app.post("/book_slot")
@jwt_required()
def book_slot():
    slot = request.json
    current_user = UUID(get_jwt_identity())

    if not slot:
        return jsonify({"error": "Missing JSON body"}), 400

    # Verifica e parsing dei dati forniti
    try:
        appointment_time_start = time.fromisoformat(slot["operator_availability_slot_start"])
        appointment_time_end = time.fromisoformat(slot["operator_availability_slot_end"])
        appointment_date = date.fromisoformat(slot["operator_availability_date"])
        availability_id = UUID(slot.get("availability_id"))
    except (KeyError, ValueError):
        return jsonify({"error": "Missing key or invalid value format"}), 400

    # Transazione atomica per verifiche e inserimento di un nuovo slot
    with Session(engine) as session:
        try:

            # deriva i dati dell'operatore, del laboratorio e del tipo di esame dalle disponibilità
            availability_query = (
                select(OperatorsAvailability)
                .where(OperatorsAvailability.availability_id == availability_id)
            )
            availability = session.execute(availability_query).scalars().first()

            laboratory_id = availability.laboratory_id
            operator_id = availability.operator_id
            exam_type_id = availability.exam_type_id

            # Verifica se l'utente ha già raggiunto il numero massimo di prenotazioni
            user_bookings_query = (
                select(SlotBooking)
                .where(SlotBooking.account_id == current_user)
                .where(SlotBooking.rejected == False)
            )  
            if len(session.execute(user_bookings_query).scalars().all()) >= MAX_BOOKINGS_PER_USER:
                return jsonify({"error": "Max bookings reached"}), 403

            # Verifica se l'utente ha già prenotato lo stesso tipo di esame anche di un altra disponibilità
            # o altro laboratorio o altro operatore
            same_exam_booked_query = (
                select(SlotBooking)
                .join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id)
                .where(SlotBooking.rejected == False)
                .where(SlotBooking.account_id == current_user)
                .where(OperatorsAvailability.exam_type_id == exam_type_id)
            )

            if session.execute(same_exam_booked_query).scalars().first():
                return jsonify({"error": "Exam type already booked"}), 403

            # Verifica se il laboratorio è chiuso nella data e ora specificate
            laboratory_closure_query = (
                select(LaboratoryClosure)
                .where(LaboratoryClosure.laboratory_id == laboratory_id)
                .where(LaboratoryClosure.start_datetime <= datetime.combine(appointment_date, appointment_time_start))
                .where(LaboratoryClosure.end_datetime > datetime.combine(appointment_date, appointment_time_start))
            )

            if session.execute(laboratory_closure_query).scalars().first():
                return jsonify({"error": "Laboratory closed"}), 409

            # Verifica se l'operatore è assente
            operator_absence_query = (
                select(OperatorAbsence)
                .where(OperatorAbsence.operator_id == operator_id)
                .where(OperatorAbsence.start_datetime <= datetime.combine(appointment_date, appointment_time_start))
                .where(OperatorAbsence.end_datetime > datetime.combine(appointment_date, appointment_time_start))
            )
            if session.execute(operator_absence_query).scalars().first():
                return jsonify({"error": "Operator absent"}), 409

            # Verifica se lo slot è ancora disponibile
            availability_query = (
                select(OperatorsAvailability)
                .where(OperatorsAvailability.availability_id == availability_id)
            )
            availability = session.execute(availability_query).scalars().first()
            if not availability:
                return jsonify({"error": "Slot not available"}), 404

            # Creazione della prenotazione
            new_booking = SlotBooking(
                account_id=current_user,
                availability_id=availability_id,
                appointment_time_start=appointment_time_start,
                appointment_time_end=appointment_time_end,
                appointment_date=appointment_date,
                rejected=False
            )
            session.add(new_booking)
            session.commit()
        
        # errore di integrità nel database
        except IntegrityError as e:
            
            session.rollback()
            logging.error("Database Error: %s\n%s", str(e), traceback.format_exc())
            return jsonify({"error": "Integrity Error"}), 400
        
        # errore generico del backend
        except Exception as e:
            session.rollback()
            logging.error(f"Unexpected error: {e}")
            return jsonify({"error": "Internal Server Error"}), 500

    return jsonify({"message": "Booking Complete"}), 200

@app.get("/slot_bookings")
@jwt_required()
def get_booked_slots():

    current_user = UUID(get_jwt_identity())

    with Session(engine) as session:

        booked_slots_query = (
            select(SlotBooking)
            .join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id)
            .where(SlotBooking.account_id == current_user)
        )
        
        booked_slots = session.execute(booked_slots_query).scalars().all()

        slots_list = []
        for slot in booked_slots:
            slots_list.append({
                "appointment_id": slot.appointment_id,
                "availability_id": slot.availability_id,
                "exam_type_id": str(slot.operators_availability.exam_type_id),
                "laboratory_id": str(slot.operators_availability.laboratory_id),
                "operator_id": str(slot.operators_availability.operator_id),
                "operator_name": slot.operators_availability.operator.name,
                "exam_type_name": slot.operators_availability.exam_type.name,
                "laboratory_name": slot.operators_availability.laboratory.name,
                "appointment_date": slot.appointment_date.isoformat(),
                "appointment_time_start": slot.appointment_time_start.isoformat(),
                "appointment_time_end": slot.appointment_time_end.isoformat(),
                "rejected": slot.rejected
            })

    return jsonify(slots_list), 200

@app.put("/book_slot/<string:appointment_id>/reject")
@jwt_required()
def reject_booked_slot(appointment_id):

    current_user = UUID(get_jwt_identity())

    try:
        appointment_id = UUID(appointment_id)
    except (ValueError):
        return jsonify({"error": "Invalid UUID Format"}), 400

    with Session(engine) as session:
        slot_query = select(SlotBooking).where(SlotBooking.appointment_id == appointment_id)
        slot = session.execute(slot_query).scalars().first()

        if not slot:
            return jsonify({"error": "Slot not found"}), 404
        
        if slot.account_id != current_user:
            logging.error(f"Current user: {current_user}, Slot account_id: {slot.account_id}")
            return jsonify({"error": "Unauthorized"}), 401

        try:
            slot.rejected = True
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logging.error("Database Error: %s\n%s", str(e), traceback.format_exc())
            return jsonify({"error": "Integrity Error"}), 400

        return jsonify({"Success": "Slot Rejected"}), 200

@app.get('/slots_availability')
@jwt_required()
def get_slots_availability():

    # Imposta i valori di default per i filtri dalla data di oggi a 60 giorni avanti
    first_reservation_datetime = datetime.combine((datetime.now() + timedelta(days=1)).date(), time(0, 0))
    last_reservation_datetime = datetime.combine((datetime.now() + timedelta(days=MAX_DAYS_BOOK_FORWARD)).date(), time(0, 0))

    # se i filtri sono presenti, sovrascrivi i valori di default se all'interno del range dei filtri di default
    try:
        if request.args.get('datetime_from_filter'):
            datetime_from_filter = max(
                datetime.fromisoformat(request.args.get('datetime_from_filter')), first_reservation_datetime)
        else:
            datetime_from_filter = first_reservation_datetime
        if request.args.get('datetime_to_filter'):
            datetime_to_filter = min(
                datetime.fromisoformat(request.args.get('datetime_to_filter')),last_reservation_datetime)
        else:
            datetime_to_filter = last_reservation_datetime 

    # se i filtri opzionali vengono passati in un formato non valido, restituisci un errore    
        exam_type_id = request.args.get('exam_type_id')
        if exam_type_id:
            exam_type_id = UUID(exam_type_id)
        operator_id = request.args.get('operator_id')
        if operator_id:
            operator_id = UUID(operator_id)
        laboratory_id = request.args.get('laboratory_id')
        if laboratory_id:
            laboratory_id = UUID(laboratory_id)

    except (ValueError):
        return jsonify({"error": "Missing key or invalid value format"}), 400

    logging.info("data inizio generazione slot: %s", datetime_from_filter)
    logging.info("data fine generazione slot: %s", datetime_to_filter)

    # tramite la sessione crea la availability_query
    with Session(engine) as session:

        # Crea la query per gli slot prenotabili
        logging.info("Esecuzione Query")
        logging.info(
        "Parametri: exam_type_id=%s, operator_id=%s, laboratory_id=%s, datetime_from_filter=%s, datetime_to_filter=%s",
             exam_type_id, operator_id, laboratory_id, datetime_from_filter, datetime_to_filter
        )

        # Crea la query per gli slot già prenotati

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
            booked_slots_query = booked_slots_query.where((OperatorsAvailability.laboratory_id) == (laboratory_id))

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
        
        logging.info("DEBUG: Availability fetched: %s", len(availability))

        try:
            slots = generate_availabile_slots(
                availability, # disponibilità degli operatori
                datetime_from_filter, # data di inizio filtro
                datetime_to_filter, # data di fine filtro          
                laboratory_closures, # periodi di chiusura dei laboratori
                operator_absences, # periodi di assenza degli operatori
                booked_slots # slot già prenotati
            )

            logging.info("Slots generated: %s", len(slots['slots']))
  
            return jsonify(slots), 200

        except Exception as e:
            logging.error("Error in slot conversion:\n%s", traceback.format_exc())
        return jsonify({"error": "Slot conversion Error"}), 500