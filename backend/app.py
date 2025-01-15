from flask import Flask, request, jsonify
from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session
from database import engine, OperatorsAvailability, Operator, Laboratory, ExamType, SlotBooking
import logging
app = Flask(__name__)

# funzione per gestire l'aggiunta di minuti ad un oggetto time. non è necessario gestire il giorno successivo
def add_minutes_to_time(original_time, minutes_to_add):
    temp_datetime = datetime.combine(date.today(), original_time)
    temp_datetime += timedelta(minutes=minutes_to_add)
    return temp_datetime.time()

   #funzione per generare slot prenotabili a partire dalle disponibilità degli operatori datetime_from_filter viene utilizzato come parametro nella route per non fornire date nel passato
def get_operator_availabilitys_slots(operators_availability, datetime_from_filter):
    # definizione dell'array che coneterrà gli slot generati
    operators_availability_slots = []
    # esamina ogni operator_availability rule
    for operator_availability in operators_availability:
        # se datetime_from_filter è impostato filtra la disponibilià degli esami partendo da quella data (se maggiore)
        if isinstance(datetime_from_filter, datetime) and datetime_from_filter.date() > operator_availability.available_from_date:
            operator_availability_date = datetime_from_filter.date()
        else:
            operator_availability_date = operator_availability.available_from_date
        # sposta operator_availability date al primo giorno della settimana indicato nella operator_availability
        operator_availability_date += timedelta(days=((operator_availability.available_weekday - operator_availability_date.weekday()) % 7))
        # per ciascun giorno fino a fine disponibilià compresa 
        while operator_availability_date <= operator_availability.available_to_date:
            # imposta la partenza del primo slot sempre all'orario di partenza delle disponibiltà
            operator_availability_slot_start = operator_availability.available_from_time
            # per ciascun giorno crea gli slot in fino all'ora di di fine disponibilità
            while operator_availability_slot_start < operator_availability.available_to_time:
                # calcola la fine dello slot
                operator_availability_slot_end = add_minutes_to_time(operator_availability_slot_start, operator_availability.slot_duration_minutes)
                # se lo slot supera l'orario esci per passare al giorno successivo
                if operator_availability_slot_end > operator_availability.available_to_time:
                   break
                # se il filtro datetime_from_filter impostato scarta lo slot se è dopo la data del filtro
                # passa allo slot successivo impostando l'orario di fine come data di inizio
                if isinstance(datetime_from_filter, datetime) and datetime.combine(operator_availability_date, operator_availability_slot_start) <= datetime_from_filter:
                    operator_availability_slot_start = add_minutes_to_time(operator_availability_slot_end, operator_availability.pause_minutes)
                    continue
                # crea lo slot come oggetto dictonary
                operator_availability_slot = {
                    "operator_availability_id": operator_availability.availability_id,
                    "exam_type_id": operator_availability.exam_type_id,
                    "laboratory_name": operator_availability.laboratory.name,
                    "operator_name": operator_availability.operator.operator_name,
                    "operator_availability_date":  operator_availability_date.isoformat(),
                    "operator_availability_slot_start": operator_availability_slot_start.isoformat(),
                    "operator_availability_slot_end": operator_availability_slot_end.isoformat()
                }
                # aggiungi lo slot all'array e passa allo slot successivo 
                operators_availability_slots.append(operator_availability_slot)
                operator_availability_slot_start = add_minutes_to_time(operator_availability_slot_end, operator_availability.pause_minutes)
            # passa alla settimana successiva
            operator_availability_date += timedelta(days=7)

    return operators_availability_slots

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
        
  
        slots_booking_query = (
        session.query(OperatorsAvailability.laboratory_id, OperatorsAvailability.operator_id, SlotBooking.appointment_id, SlotBooking.availability_id, SlotBooking.appointment_datetime_start, SlotBooking.appointment_datetime_end, SlotBooking.exam_type_id, SlotBooking.rejected)
        .join(OperatorsAvailability, SlotBooking.availability_id == OperatorsAvailability.availability_id)
    )

        slots_booking_query = slots_booking_query.filter(SlotBooking.rejected == False)
        slots_booking_query = slots_booking_query.filter(SlotBooking.appointment_datetime_end >= datetime_from_filter.date())

        # Filtra la slots_booking_query in base ai parametri opzionali
        if exam_type_id:
            slots_booking_query = slots_booking_query.filter(SlotBooking.exam_type_id == exam_type_id)
        if operator_id:
            slots_booking_query = slots_booking_query.filter(SlotBooking.operator.operator_id == operator_id)
        if laboratory_id:
            slots_booking_query = slots_booking_query.filter(SlotBooking.laboratory.laboratory_id == laboratory_id)
        
        booked_slots = slots_booking_query.all()
        
        
        
        
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

        availability_results = availability_query.all()


        for availability in availability_results:
            print(
                "Availability ID:", availability.availability_id,
                "| Operator:", availability.operator.operator_name,
                "| Laboratory:", availability.laboratory.name
            )
        
        try:
            slots = get_operator_availabilitys_slots(availability_results, datetime_from_filter)
            return jsonify(slots), 200
        except Exception as e:
            # Log dell'errore con stack trace
            logging.error("Error in slot conversion: %s", str(e))
            return jsonify({"error": "Slot conversion Error"}), 500
        