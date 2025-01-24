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
from flask import blueprints

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
    logging.info(f"Verifica blocklist per JTI {jti}: {'Bloccato' if is_blocked else 'Non bloccato'}")
    return is_blocked


@app.post("/register")
def register():
 
    new_account = request.json
    if not new_account:
        return jsonify({"Request invalid":"missing JSON body"}), 400

    #Caratteri e numeri da 6 a 30 caratteri
    username_regex = r'^[0-9A-Za-z]{6,30}$'
    #Almeno una lettera maiuscola, una minuscola, un numero e un simbolo lunghezza da 8 a 32 caratteri
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,32}$'
    #Email valida
    email_regex    = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    #Numero di telefono internazionale
    tel_number_regex = r'^\+?\d{10,13}$'

    if not re.match(username_regex, new_account.get("username", "")):
        return jsonify({"error": "Invalid username"}), 400
    if not re.match(password_regex, new_account.get("password", "")):
        return jsonify({"error": "Invalid password"}), 400
    if not re.match(email_regex, new_account.get("email", "")):
        return jsonify({"error": "Invalid email"}), 400
    if not re.match(tel_number_regex, new_account.get("tel_number", "")):
        return jsonify({"error": "Invalid tel_number"}), 400
    
    new_account = Account(
        username=new_account.get("username"),
        password_hash = generate_password_hash(new_account.get("password")),
        email=new_account.get("email"),
        tel_number=new_account.get("tel_number"),
        first_name=new_account.get("first_name"),
        last_name=new_account.get("last_name")
    )

    with Session(engine) as session:
        
        # verifica eventuali username o email già presenti nel database
        username_query = select(Account).where(Account.username == new_account.username)
        if session.execute(username_query).scalars().first():
            return jsonify({"error": "Username already in use"}), 409
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
#@csrf.exempt
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
            resp = make_response({"message": "Logged in"})
            set_access_cookies(resp, access_token)
            return resp
        
        else:
            account.failed_login_count = account.failed_login_count + 1
            account.last_failed_login = datetime.now()
            session.commit()

            return jsonify({"error": "Invalid username or password"}), 401

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
            "username": account.username,
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

@app.get("/operators")
@jwt_required()
def get_operators():

    try:
        exam_id = request.args.get("exam_id")
        laboratory_id = request.args.get("laboratory_id")

        if exam_id:
            exam_id = UUID(exam_id)
        if laboratory_id:
            laboratory_id = UUID(laboratory_id)

    except (ValueError):
        return jsonify({"error": "Invalid UUID Format"}), 400

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
                "operator_id": str(operator.operator_id),
                "name": operator.name
            })

    return jsonify(operators_list), 200

@app.get("/exam_types")
@jwt_required()
def get_exam_types():

    with Session(engine) as session:

        exam_types_query = select(ExamType)
        exam_types = session.execute(exam_types_query).scalars().all()

        exam_types_list = []
        for exam_type in exam_types:
            exam_types_list.append({
                "exam_type_id": str(exam_type.exam_type_id),
                "name": exam_type.name,
                "description": exam_type.description
            })

    return jsonify(exam_types_list), 200

@app.get("/laboratories")
@jwt_required()
def get_laboratories():
    
    try:
        exam_id = request.args.get("exam_id")
        operator_id = request.args.get("operator_id")

        if exam_id:
            exam_id = UUID(exam_id)
        if operator_id:
            operator_id = UUID(operator_id)
    except (ValueError):
        return jsonify({"error": "Invalid UUID Format"}), 400
    

    with Session(engine) as session:
        
        laboratories_query = select(Laboratory).join(OperatorsAvailability, Laboratory.laboratory_id == OperatorsAvailability.laboratory_id).distinct()

        if exam_id:
            laboratories_query = laboratories_query.where(OperatorsAvailability.exam_type_id == exam_id)
        if operator_id:
            laboratories_query = laboratories_query.where(OperatorsAvailability.operator_id == operator_id)

        laboratories = session.execute(laboratories_query).scalars().all()

        labs_list = []
        for laboratory in laboratories:
            labs_list.append({
                "laboratory_id": str(laboratory.laboratory_id),
                "name": laboratory.name,
                "address": laboratory.address,
                "contact_info": laboratory.contact_info
            })

    return jsonify(labs_list), 200

@app.post("/book_slot")
@jwt_required()
def book_slot():

    slot = request.json
    current_user = UUID(get_jwt_identity())

    if not slot:
        return jsonify({"error": "Missing JSON body"}), 400
    
    # verifica la presenza di tutti i campi obbligatori necessari per la prenotazione
    try:
        appointment_time_start = time.fromisoformat(slot["operator_availability_slot_start"])
        appointment_time_end  =time.fromisoformat(slot["operator_availability_slot_end"])
        appointment_date = date.fromisoformat(slot["operator_availability_date"])
        availability_id = UUID(slot.get("availability_id"))
        exam_type_id = UUID(slot.get("exam_type_id"))

    except (KeyError, ValueError):
        return jsonify({"error": "Missing key or invalid value format"}), 400

    with Session(engine) as session:

        # non è possibile prenotare lo stesso esame due volte
        booked_slots_query = (
            select(SlotBooking)
            .join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id)
            .where(SlotBooking.rejected == False)
            .where(SlotBooking.account_id == current_user)
            .where(OperatorsAvailability.exam_type_id == exam_type_id)
        )
        # vincolo applicativo un utente non può prenotare più volte lo stesso esame
        # viene utilizzato un codice specifico per utilizzare un messaggio specifico in forntend
        same_exam_booked = session.execute(booked_slots_query).scalars().all()
        if same_exam_booked:
            return jsonify({"error": "exam type already booked"}), 409 

        new_booking = SlotBooking(
            account_id=current_user,
            availability_id=availability_id,
            appointment_time_start = appointment_time_start,
            appointment_time_end = appointment_time_end,
            appointment_date = appointment_date,
            rejected=False
        )

        try:
            session.add(new_booking)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logging.error("Database Error: %s\n%s", str(e), traceback.format_exc())
            return jsonify({"error": "Integrity Error"}), 400
        
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