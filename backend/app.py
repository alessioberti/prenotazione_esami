from .operators_availability import generate_availabile_slots
from flask import Flask, request, jsonify
from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session
from database import engine, OperatorsAvailability, Operator, Laboratory, SlotBooking, LaboratoryClosure, OperatorAbsence
import logging
app = Flask(__name__)

@app.route('/api/slots_availability', methods=['GET'])
def get_slots_availability():
    # Restituisci le disponibilità da una data specifca
    datetime_from_filter = request.args.get('datetime_from_filter')
    # Restituisci le disponibilità di un esame specifico
    exam_type_id = request.args.get('exam_type_id', type=int)
    # Restituisci le disponibilità di un operatore specifico
    operator_id = request.args.get('operator_id', type=int)
    # Restituisci le disponibilità di un laboratorio specifico
    laboratory_id = request.args.get('laboratory_id', type=int)

    # Imposta un controllo sulla data di partenza della verifica delle disponibilità che non può essere nel passato o nel giorno corrente
    # può essere richiesta la disponibità dalla data successiva alla data odierna
    first_reservation_datetime = datetime.combine(datetime.now().date() + timedelta(days=1), time(0, 6))
    if datetime_from_filter:
        try:
            # usa la maggiore tra la data di partenza delle disponibilità inserita tramite api e la data di next day impostata precedentemente
            datetime_from_filter = max((datetime.strptime(datetime_from_filter, '%Y-%m-%d %H:%M:%S').date()), first_reservation_datetime.date())
        except ValueError:
            return jsonify({"error": "Invalid datetime format. Use YYYY-MM-DD HH:MM:SS"}), 400
    else:
        datetime_from_filter = first_reservation_datetime

    # tramite la sessione crea la availability_query
    with Session(engine) as session:
        
  
        booked_slots_query = session.query(
            OperatorsAvailability.laboratory_id, OperatorsAvailability.operator_id, OperatorsAvailability.exam_type_id,
            SlotBooking.appointment_id, SlotBooking.availability_id, SlotBooking.appointment_datetime_start, SlotBooking.appointment_datetime_end, SlotBooking.rejected
            ).join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id
        )
        
        booked_slots_query = booked_slots_query.filter(SlotBooking.rejected == False)
        booked_slots_query = booked_slots_query.filter(SlotBooking.appointment_datetime_end >= datetime_from_filter.date())

        if exam_type_id:
            booked_slots_query = booked_slots_query.filter(SlotBooking.operators_availability.exam_type_id == exam_type_id)
        if operator_id:
            booked_slots_query = booked_slots_query.filter(SlotBooking.operators_availability.operator_id == operator_id)
        if laboratory_id:
            booked_slots_query = booked_slots_query.filter(SlotBooking.operators_availability.laboratory_id == laboratory_id)
        

        # Crea la query per i periodi di chiusura dei laboratori

        laboratory_closures_query = (
            session.query(Laboratory.laboratory_id, LaboratoryClosure.start_datetime, LaboratoryClosure.end_datetime)
            .join(LaboratoryClosure, Laboratory.laboratory_id == LaboratoryClosure.laboratory_id)
        )   

        laboratory_closures_query = laboratory_closures_query.filter(LaboratoryClosure.end_datetime >= datetime_from_filter.date())
        
        if laboratory_id:
            laboratory_closures_query = laboratory_closures_query.filter(Laboratory.laboratory_id == laboratory_id)
        
        # Crea la query per i periodi di assenza degli operatori

        operator_absences_query = (
            session.query(Operator.operator_id, OperatorAbsence.start_datetime, OperatorAbsence.end_datetime)
            .join(OperatorAbsence, Operator.operator_id == OperatorAbsence.operator_id)
        )  

        operator_absences_query = operator_absences_query.filter(OperatorAbsence.end_datetime >= datetime_from_filter.date())
        if operator_id:
            operator_absences_query = operator_absences_query.filter(Operator.operator_id == operator_id)
        
        availability_query = (
            session.query(OperatorsAvailability)
            .join(OperatorsAvailability.operator)
            .join(OperatorsAvailability.laboratory)
            .join(OperatorsAvailability.exam_type)
        )

        # Filtra la availability_query in base ai parametri obbligatori la disponibilità deve essere attiva e la data di inizio deve esseere compresa tra la data di inizio e fine della disponibilità
        availability_query = availability_query.filter(OperatorsAvailability.enabled == True)
        availability_query = availability_query.filter(OperatorsAvailability.available_from_date <= datetime_from_filter.date())
        availability_query = availability_query.filter(OperatorsAvailability.available_to_date >= datetime_from_filter.date())

        # Filtra la availability_query in base ai parametri opzionali
        if exam_type_id:
            availability_query = availability_query.filter(OperatorsAvailability.exam_type_id == exam_type_id)
        if operator_id:
            availability_query = availability_query.filter(OperatorsAvailability.operator.operator_id == operator_id)
        if laboratory_id:
            availability_query = availability_query.filter(OperatorsAvailability.laboratory.laboratory_id == laboratory_id)

        try:
            slots = generate_availabile_slots(availability_query.all(), datetime_from_filter, laboratory_closures_query.all(), operator_absences_query.all(), booked_slots_query.all())
            return jsonify(slots), 200
        except Exception as e:
            # Log dell'errore con stack trace
            logging.error("Error in slot conversion: %s", str(e))
            return jsonify({"error": "Slot conversion Error"}), 500
        