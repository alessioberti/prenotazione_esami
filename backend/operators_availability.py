from datetime import date, datetime, time, timedelta

# funzione per gestire l'aggiunta di minuti ad un oggetto time. non è necessario gestire il giorno successivo
def add_minutes_to_time(original_time, minutes_to_add):
    temp_datetime = datetime.combine(date.today(), original_time)
    temp_datetime += timedelta(minutes=minutes_to_add)
    return temp_datetime.time()

#funzione per verificare se uno slot è già stato prenotato
def slot_is_booked(slot, booked_slots):
    for booked_slot in booked_slots:
        if (
            slot["operator_availability_id"] == booked_slot["operator_availability_id"] and 
            datetime.combine(slot["operator_availability_date"], slot["operator_availability_slot_start"]) == booked_slot.appointment_datetime_start and
            datetime.combine(slot["operator_availability_date"], slot["operator_availability_slot_end"]) == booked_slot.appointment_datetime_end):   
      
            return True
    return False

#funzione per verificare se uno slot è in un periodo di chiusura di un laboratorio 
def lab_is_closed(slot, laboratory_closures):
    for laboratory_closure in laboratory_closures:
        if slot["laboratory_id"] == laboratory_closure["laboratory_id"]:
            if datetime.combine(slot["operator_availability_date"],slot["operator_availability_slot_start"]) < laboratory_closure["end_datetime"] and datetime.combine(slot["operator_availability_date"],slot["operator_availability_slot_end"]) > laboratory_closure["start_datetime"]:
                return True
    return False

#funzione per verificare se uno slot è in un periodo di assenza di un operatore 
def operator_is_absent(slot, operator_absences):
    for operator_absence in operator_absences:
        if slot["operator_id"] == operator_absence["operator_id"]:
            if datetime.combine(slot["operator_availability_date"],slot["operator_availability_slot_start"]) < operator_absence["end_datetime"] and datetime.combine(slot["operator_availability_date"],slot["operator_availability_slot_end"]) > operator_absence["start_datetime"]:
                return True
    return False

#funzione per generare slot prenotabili a partire dalle disponibilità degli operatori datetime_from_filter viene utilizzato come parametro nella route per non fornire date nel passato
def generate_availabile_slots(operators_availability, datetime_from_filter = None, laboratory_closures = None, operator_absences = None, booked_slots = None):
    # definizione dell'array che coneterrà gli slot generati
    operators_availability_slots = []
    # esamina ogni operator_availability rule
    for operator_availability in operators_availability:
        # se datetime_from_filter è impostato filtra la disponibilià degli esami partendo da quella data (se maggiore)
        if  isinstance(datetime_from_filter, datetime) and datetime_from_filter.date() > operator_availability.available_from_date:
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
                # se lo slot supera l'orario esci e passa alla settimana successiva
                if operator_availability_slot_end > operator_availability.available_to_time:
                   break
                
                # crea lo slot come oggetto dictonary
                slot = {
                    "operator_availability_id": operator_availability.availability_id,
                    "exam_type_id": operator_availability.exam_type_id,
                    "laboratory_id":operator_availability.laboratory_id,
                    "operator_id":operator_availability.operator_id,
                    "exam_type_name": operator_availability.exam_type.name,
                    "laboratory_name": operator_availability.laboratory.name,
                    "operator_name": operator_availability.operator.name,
                    "operator_availability_date":  operator_availability_date.isoformat(),
                    "operator_availability_slot_start": operator_availability_slot_start.isoformat(),
                    "operator_availability_slot_end": operator_availability_slot_end.isoformat()
                }

                # se lo slot è dopo l'orario del filtro e se è il laboratorio non è chiuso l'oepratore in ferie e lo slot non è già prenotato
                if (
                    ((datetime_from_filter == None) or (datetime.combine(operator_availability_date, operator_availability_slot_start) >= datetime_from_filter)) and
                    ((laboratory_closures == None) or (not lab_is_closed(slot,laboratory_closures))) and 
                    ((operator_absences == None) or (not operator_is_absent(slot,operator_absences))) and 
                    ((booked_slots == None) or (not slot_is_booked(slot,booked_slots)))):
                    
                    # aggiungi lo slot all'array
                    operators_availability_slots.append(slot)

                #passa allo slot successivo
                operator_availability_slot_start = add_minutes_to_time(operator_availability_slot_end, operator_availability.pause_minutes)
            # passa alla settimana successiva
            operator_availability_date += timedelta(days=7)

    return operators_availability_slots