from operators_availability import generate_availabile_slots
from flask import Flask, request, jsonify
from datetime import date, datetime, time, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import engine, OperatorsAvailability, Operator, Laboratory, SlotBooking, LaboratoryClosure, OperatorAbsence, ExamType
import logging, traceback


exam_type_id = None
operator_id = None
laboratory_id = None
datetime_from_filter = "2025-09-01 00:00:00"

first_reservation_datetime = datetime.combine(datetime.now().date() + timedelta(days=1), time(0, 6))

if datetime_from_filter:
    try:
        # usa la maggiore tra la data di partenza delle disponibilità inserita tramite api e la data di next day impostata precedentemente
        datetime_from_filter = max((datetime.strptime(datetime_from_filter, '%Y-%m-%d %H:%M:%S')), first_reservation_datetime)
    except ValueError:
        logging.error("Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
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
        laboratory_closures_query = laboratory_closures_query.where(LaboratoryClosure.start_datetime >= datetime_from_filter)
    if laboratory_id:
        laboratory_closures_query = laboratory_closures_query.where(LaboratoryClosure.laboratory_id == laboratory_id)
    laboratory_closures = session.execute(laboratory_closures_query).scalars().all()
    # Crea la query per i periodi di assenza degli operatori
    operator_absences_query  = select(OperatorAbsence)
    if datetime_from_filter:
        operator_absences_query = operator_absences_query.where(OperatorAbsence.start_datetime >= datetime_from_filter)
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
        availability_query = availability_query.where(OperatorsAvailability.available_from_date >= datetime_from_filter.date())
    if exam_type_id:
        availability_query = availability_query.where(OperatorsAvailability.exam_type_id == exam_type_id)
    if operator_id:
        availability_query = availability_query.where(OperatorsAvailability.operator_id == operator_id)
    if laboratory_id:
        availability_query = availability_query.where(OperatorsAvailability.laboratory_id == laboratory_id)
    availability = session.execute(availability_query).scalars().all()

    slots = generate_availabile_slots(availability, datetime_from_filter, laboratory_closures, operator_absences, booked_slots)
    logging.info("Slots generated: %s", len(slots))