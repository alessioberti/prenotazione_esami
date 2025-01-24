import os
import uuid
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Date, Time, DateTime, Boolean, Integer, Index, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, time
from dotenv import load_dotenv

#https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#tutorial-working-with-metadata
#https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
load_dotenv()

try:
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_ECHO = bool(os.getenv("POSTGRES_ECHO", "False") == "True")
    
except KeyError as e:
    print(f"Errore: variabile d'ambiente necesaria per l'avvio del database: {e}")
    exit(1)

engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}", echo=POSTGRES_ECHO)

from sqlalchemy.dialects.postgresql import VARCHAR

class Base(DeclarativeBase):
    pass

# Tabella Gestione degli account 
class Account(Base):
    __tablename__ = "account"

    # viene utilizzato uuid in quanto jwt richiede un campo stringa univoco 
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    tel_number: Mapped[str] = mapped_column(String(30))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    last_failed_login: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    is_operator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relazioni
    operator: Mapped["Operator"] = relationship(back_populates="account")

# Tabella gestione Laboratori
class Laboratory(Base):
    __tablename__ = "laboratories"

    laboratory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    contact_info: Mapped[Optional[str]] = mapped_column(String(255))

    # Relazione con OperatorsAvailability
    operators_availability: Mapped[List["OperatorsAvailability"]] = relationship(
        back_populates="laboratory"
    )

# Tabella giorni di chiusura dei laboratori
class LaboratoryClosure(Base):
    __tablename__ = "laboratory_closures"

    closure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    laboratory_id: Mapped[str] = mapped_column(ForeignKey("laboratories.laboratory_id"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

# Tabella di gestione dei tipi di esame
class ExamType(Base):
    __tablename__ = "exam_types"

    exam_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)

    operators_availability: Mapped[List["OperatorsAvailability"]] = relationship(
        back_populates="exam_type"
    )

# Tabella per la gestione degli operatori
class Operator(Base):
    __tablename__ = "operators"

    operator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[str] = mapped_column(ForeignKey("account.account_id"), nullable=False)

    # Relazioni
    account: Mapped["Account"] = relationship(back_populates="operator")
    operators_availability: Mapped[List["OperatorsAvailability"]] = relationship(
        back_populates="operator"
    )
    
# Tabella per la gestione delle assenze
class OperatorAbsence(Base):
    __tablename__ = "operator_absences"

    absence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operators.operator_id"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

# Tabella Disponibilità
class OperatorsAvailability(Base):
    __tablename__ = "operators_availability"

    availability_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    exam_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_types.exam_type_id"), nullable=False)
    laboratory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("laboratories.laboratory_id"), nullable=False)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operators.operator_id"), nullable=False)
    available_from_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_to_date: Mapped[date] = mapped_column(Date, nullable=False)
    available_from_time: Mapped[time] = mapped_column(Time, nullable=False)
    available_to_time: Mapped[time] = mapped_column(Time, nullable=False)
    available_weekday: Mapped[int] = mapped_column(nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(nullable=False)
    pause_minutes: Mapped[int] = mapped_column(nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relazioni
    laboratory: Mapped["Laboratory"] = relationship(back_populates="operators_availability")
    operator: Mapped["Operator"] = relationship(back_populates="operators_availability")
    exam_type: Mapped["ExamType"] = relationship(back_populates="operators_availability")
    slot_bookings: Mapped[List["SlotBooking"]] = relationship(back_populates="operators_availability")

# Tabella per la gestione delle prenotazioni
class SlotBooking(Base):
    __tablename__ = "slot_bookings"

    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account.account_id"))
    availability_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operators_availability.availability_id"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time_start: Mapped[time] = mapped_column(Time, nullable=False)
    appointment_time_end: Mapped[time] = mapped_column(Time, nullable=False)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relazioni
    operators_availability: Mapped["OperatorsAvailability"] = relationship(back_populates="slot_bookings")

    # Vincolo necessario per evitare le duplicazioni di due prenotazioni attive
    __table_args__ = (
        Index(
            "uq_active_appointments",
            "availability_id",
            "appointment_date",
            "appointment_time_start",
            unique=True,
            postgresql_where=text("NOT rejected"),
        ),
    )

Base.metadata.create_all(engine)

def clear_existing_data():
    with Session(engine) as session:
        # Cancella tutte le tabelle correlate
        session.query(SlotBooking).delete()
        session.query(OperatorsAvailability).delete()
        session.query(OperatorAbsence).delete()
        session.query(Operator).delete()
        session.query(ExamType).delete()
        session.query(LaboratoryClosure).delete()
        session.query(Laboratory).delete()
        session.query(Account).delete()
        session.commit()
        print("Dati esistenti rimossi.")

def populate_demo_data():
    try:
        with Session(engine) as session:
            # === 1. Creazione Account ===
            account_uuids = {
                "marco_rossi": uuid.uuid4(),
                "giulia_verdi": uuid.uuid4(),
                "luca_bianchi": uuid.uuid4(),
                "sara_neri": uuid.uuid4()
            }
            accounts = [
                Account(
                    account_id=account_uuids["marco_rossi"],
                    password_hash="hashed_password1",
                    email="marco.rossi@example.com",
                    first_name="Marco",
                    last_name="Rossi",
                    tel_number="+393451234567",
                    enabled=True,
                    failed_login_count=0,
                    is_operator=True,
                    is_admin=False,
                ),
                Account(
                    account_id=account_uuids["giulia_verdi"],
                    password_hash="hashed_password2",
                    email="giulia.verdi@example.com",
                    first_name="Giulia",
                    last_name="Verdi",
                    tel_number="+393487654321",
                    enabled=True,
                    failed_login_count=0,
                    is_operator=False,
                    is_admin=True,
                ),
                Account(
                    account_id=account_uuids["luca_bianchi"],
                    password_hash="hashed_password3",
                    email="luca.bianchi@example.com",
                    first_name="Luca",
                    last_name="Bianchi",
                    tel_number="+393479876543",
                    enabled=True,
                    failed_login_count=0,
                    is_operator=True,
                    is_admin=False,
                ),
                Account(
                    account_id=account_uuids["sara_neri"],
                    password_hash="hashed_password4",
                    email="sara.neri@example.com",
                    first_name="Sara",
                    last_name="Neri",
                    tel_number="+393461234987",
                    enabled=True,
                    failed_login_count=0,
                    is_operator=True,
                    is_admin=False,
                ),
            ]
            session.add_all(accounts)

            # === 2. Creazione Laboratori ===
            laboratory_uuids = {
                "milano": uuid.uuid4(),
                "torino": uuid.uuid4(),
                "roma": uuid.uuid4(),
                "napoli": uuid.uuid4()
            }
            laboratories = [
                Laboratory(
                    laboratory_id=laboratory_uuids["milano"],
                    name="Laboratorio Sanità Milano",
                    address="Via Roma 10, Milano",
                    contact_info="info.milano@laboratori.it",
                ),
                Laboratory(
                    laboratory_id=laboratory_uuids["torino"],
                    name="Centro Analisi Torino",
                    address="Corso Francia 25, Torino",
                    contact_info="info.torino@laboratori.it",
                ),
                Laboratory(
                    laboratory_id=laboratory_uuids["roma"],
                    name="Clinica Roma",
                    address="Via Nazionale 15, Roma",
                    contact_info="info.roma@laboratori.it",
                ),
                Laboratory(
                    laboratory_id=laboratory_uuids["napoli"],
                    name="Laboratorio Napoli",
                    address="Piazza Garibaldi 20, Napoli",
                    contact_info="info.napoli@laboratori.it",
                ),
            ]
            session.add_all(laboratories)

            # === 3. Creazione Tipi di Esame ===
            exam_type_uuids = {
                "esame_sangue": uuid.uuid4(),
                "tampone": uuid.uuid4(),
                "ecg": uuid.uuid4(),
                "radiografia": uuid.uuid4()
            }
            exam_types = [
                ExamType(
                    exam_type_id=exam_type_uuids["esame_sangue"],
                    name="Esame del Sangue",
                    description="Analisi ematica completa",
                ),
                ExamType(
                    exam_type_id=exam_type_uuids["tampone"],
                    name="Tampone Molecolare",
                    description="Test molecolare per COVID-19",
                ),
                ExamType(
                    exam_type_id=exam_type_uuids["ecg"],
                    name="ECG",
                    description="Elettrocardiogramma",
                ),
                ExamType(
                    exam_type_id=exam_type_uuids["radiografia"],
                    name="Radiografia",
                    description="Radiografia standard",
                ),
            ]
            session.add_all(exam_types)

            # === 4. Creazione Operatori ===
            operator_uuids = {
                "francesca_conti": uuid.uuid4(),
                "alessandro_ricci": uuid.uuid4(),
                "luca_bianchi": uuid.uuid4(),
                "sara_neri": uuid.uuid4()
            }
            operators = [
                Operator(
                    operator_id=operator_uuids["francesca_conti"],
                    name="Dott.ssa Francesca Conti",
                    account_id=account_uuids["marco_rossi"],
                ),
                Operator(
                    operator_id=operator_uuids["alessandro_ricci"],
                    name="Specialista Alessandro Ricci",
                    account_id=account_uuids["giulia_verdi"],
                ),
                Operator(
                    operator_id=operator_uuids["luca_bianchi"],
                    name="Dott. Luca Bianchi",
                    account_id=account_uuids["luca_bianchi"],
                ),
                Operator(
                    operator_id=operator_uuids["sara_neri"],
                    name="Specialista Sara Neri",
                    account_id=account_uuids["sara_neri"],
                ),
            ]
            session.add_all(operators)

            # === 5. Creazione Disponibilità ===
            availability_uuids = {
                "francesca_lunedi": uuid.uuid4(),
                "alessandro_mercoledi": uuid.uuid4(),
                "luca_venerdi": uuid.uuid4(),
                "sara_martedi": uuid.uuid4(),
                "francesca_giovedi": uuid.uuid4()
            }
            availabilities = [
                OperatorsAvailability(
                    availability_id=availability_uuids["francesca_lunedi"],
                    operator_id=operator_uuids["francesca_conti"],
                    laboratory_id=laboratory_uuids["milano"],
                    exam_type_id=exam_type_uuids["esame_sangue"],
                    available_from_date=date(2025, 1, 22),
                    available_to_date=date(2025, 1, 31),
                    available_from_time=time(9, 0),
                    available_to_time=time(17, 0),
                    available_weekday=1,
                    slot_duration_minutes=30,
                    pause_minutes=10,
                    enabled=True,
                ),
                OperatorsAvailability(
                    availability_id=availability_uuids["alessandro_mercoledi"],
                    operator_id=operator_uuids["alessandro_ricci"],
                    laboratory_id=laboratory_uuids["torino"],
                    exam_type_id=exam_type_uuids["tampone"],
                    available_from_date=date(2025, 1, 22),
                    available_to_date=date(2025, 1, 31),
                    available_from_time=time(8, 30),
                    available_to_time=time(12, 30),
                    available_weekday=3,
                    slot_duration_minutes=20,
                    pause_minutes=5,
                    enabled=True,
                ),
                OperatorsAvailability(
                    availability_id=availability_uuids["luca_venerdi"],
                    operator_id=operator_uuids["luca_bianchi"],
                    laboratory_id=laboratory_uuids["roma"],
                    exam_type_id=exam_type_uuids["ecg"],
                    available_from_date=date(2025, 1, 22),
                    available_to_date=date(2025, 1, 31),
                    available_from_time=time(9, 0),
                    available_to_time=time(13, 0),
                    available_weekday=5,
                    slot_duration_minutes=15,
                    pause_minutes=5,
                    enabled=True,
                ),
                OperatorsAvailability(
                    availability_id=availability_uuids["sara_martedi"],
                    operator_id=operator_uuids["sara_neri"],
                    laboratory_id=laboratory_uuids["napoli"],
                    exam_type_id=exam_type_uuids["radiografia"],
                    available_from_date=date(2025, 1, 22),
                    available_to_date=date(2025, 1, 31),
                    available_from_time=time(10, 0),
                    available_to_time=time(14, 0),
                    available_weekday=2,
                    slot_duration_minutes=25,
                    pause_minutes=10,
                    enabled=True,
                ),
                OperatorsAvailability(
                    availability_id=availability_uuids["francesca_giovedi"],
                    operator_id=operator_uuids["francesca_conti"],
                    laboratory_id=laboratory_uuids["milano"],
                    exam_type_id=exam_type_uuids["radiografia"],
                    available_from_date=date(2025, 1, 22),
                    available_to_date=date(2025, 1, 31),
                    available_from_time=time(14, 0),
                    available_to_time=time(18, 0),
                    available_weekday=4,
                    slot_duration_minutes=20,
                    pause_minutes=5,
                    enabled=True,
                ),
            ]
            session.add_all(availabilities)
            session.commit()
    except Exception as e:
        print(f"Errore durante la generazione dei dati demo: {e}")
        session.rollback()

#clear_existing_data()
#populate_demo_data()
