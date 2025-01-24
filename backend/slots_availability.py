import os
from uuid import UUID
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.orm import Session 
from datetime import date, datetime, time, timedelta
import logging, traceback
from database import engine, OperatorsAvailability, Operator, Laboratory, SlotBooking, LaboratoryClosure, OperatorAbsence, ExamType
from generate_availabile_slots import generate_availabile_slots

# funzione per la paginazione
#https://stackoverflow.com/questions/17777845/python-requests-arguments-dealing-with-api-pagination

def paginate(data, page, page_size):
    if page < 1 or page_size < 1:
        raise ValueError("Page and page_size must be greater than 0")
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    return data[start_index:end_index]

@app.get('/slots_availability/offset/<int:offset>/limit/<int:limit>')
@jwt_required()
def get_slots_availability(offset, limit):

    # Imposta i valori di default per i filtri dalla data di oggi a 60 giorni avanti
    
    first_reservation_datetime = datetime.combine((datetime.now() + timedelta(days=1)).date(), time(0, 0))
    last_reservation_datetime = datetime.combine((datetime.now() + timedelta(days=365)).date(), time(0, 0))

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

        exam_type_id = request.args.get('exam_type_id', type=int)
        if exam_type_id:
            exam_type_id = UUID(exam_type_id)
        operator_id = request.args.get('operator_id', type=int)
        if operator_id:
            operator_id = UUID(operator_id)
        laboratory_id = request.args.get('laboratory_id', type=int)
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
            slots = generate_availabile_slots(
                availability, # disponibilità degli operatori
                datetime_from_filter, # data di inizio filtro
                datetime_to_filter, # data di fine filtro          
                laboratory_closures, # periodi di chiusura dei laboratori
                operator_absences, # periodi di assenza degli operatori
                booked_slots # slot già prenotati 
            )

            logging.info("Slots generated: %s", len(slots))
               
            # paginazione dell'output   
              
            paginated_slots = slots[offset:offset + limit]
            
            return jsonify({
                "offset": offset,
                "limit": limit,
                "total_slots": len(slots),
                "slots": paginated_slots
            }), 200        
 
            

            
        except Exception as e:
            logging.error("Error in slot conversion:\n%s", traceback.format_exc())
            return jsonify({"error": "Slot conversion Error"}), 500
