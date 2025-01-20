from typing import List, Optional
from sqlalchemy import ForeignKey, String, Date, Time, DateTime, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, time
import uuid

#https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#tutorial-working-with-metadata
#https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login

class Base(DeclarativeBase):
    pass


# Tabella Gestione degli account 
class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    #account_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    tel_number: Mapped[str] = mapped_column(String(30))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    last_failed_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

# Tabella gestione Laboratori
class Laboratory(Base):
    __tablename__ = "laboratories"

    laboratory_id: Mapped[int] = mapped_column(primary_key=True)
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

    closure_id: Mapped[int] = mapped_column(primary_key=True)
    laboratory_id: Mapped[int] = mapped_column(ForeignKey("laboratories.laboratory_id"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

# Tabella di gestione dei tipi di esame
class ExamType(Base):
    __tablename__ = "exam_types"

    exam_type_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)

    operators_availability: Mapped[List["OperatorsAvailability"]] = relationship(
        back_populates="exam_type"
    )

# Tabella per la gestione degli operatori
class Operator(Base):
    __tablename__ = "operators"

    operator_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    operators_availability: Mapped[List["OperatorsAvailability"]] = relationship(
        back_populates="operator"
    )

# Tabella per la gestione delle assenze
class OperatorAbsence(Base):
    __tablename__ = "operator_absences"

    absence_id: Mapped[int] = mapped_column(primary_key=True)
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.operator_id"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class OperatorsAvailability(Base):
    __tablename__ = "operators_availability"

    availability_id: Mapped[int] = mapped_column(primary_key=True)
    exam_type_id: Mapped[int] = mapped_column(ForeignKey("exam_types.exam_type_id"), nullable=False)
    laboratory_id: Mapped[int] = mapped_column(ForeignKey("laboratories.laboratory_id"), nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey("operators.operator_id"), nullable=False)
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

    appointment_id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("account.account_id"))
    availability_id: Mapped[int] = mapped_column(ForeignKey("operators_availability.availability_id"), nullable=False)
    appointment_datetime_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    appointment_datetime_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relazioni
    operators_availability: Mapped["OperatorsAvailability"] = relationship(back_populates="slot_bookings")

engine = create_engine("sqlite:///database.db", echo=False)

Base.metadata.create_all(engine)


with Session(engine) as session:

    try:

        # Inserimento degli account
        mrossi = Account(username="mrossi", password_hash="hashpassword1", email="marco.rossi@example.com", tel_number="3401234567")
        gverdi = Account(username="gverdi", password_hash="hashpassword2", email="giulia.verdi@example.com", tel_number="3402345678")
        albianchi = Account(username="albianchi", password_hash="hashpassword3", email="alessandro.bianchi@example.com", tel_number="3403456789")
        esantini = Account(username="esantini", password_hash="hashpassword4", email="elena.santini@example.com", tel_number="3404567890")
        clombardi = Account(username="clombardi", password_hash="hashpassword5", email="carlo.lombardi@example.com", tel_number="3405678901")
    
        session.add_all([mrossi, gverdi, albianchi, esantini, clombardi])
    
        # Inserimento degli operatori
        op_marco = Operator(operator_id=1, name="Marco Rossi")
        op_giulia = Operator(operator_id=2, name="Giulia Verdi")
        op_alessandro = Operator(operator_id=3, name="Alessandro Bianchi")
        op_elena = Operator(operator_id=4, name="Elena Santini")
        op_carlo = Operator(operator_id=5, name="Carlo Lombardi")
    
        session.add_all([op_marco, op_giulia, op_alessandro, op_elena, op_carlo])
    
        # Inserimento dei laboratori
        lab_milano = Laboratory(name="Laboratorio Milano", address="Via Milano 10, Milano", contact_info="info.milano@laboratori.it")
        lab_roma = Laboratory(name="Laboratorio Roma", address="Via Appia 20, Roma", contact_info="info.roma@laboratori.it")
        lab_torino = Laboratory(name="Laboratorio Torino", address="Corso Italia 15, Torino", contact_info="info.torino@laboratori.it")
        lab_firenze = Laboratory(name="Laboratorio Firenze", address="Piazza Duomo 5, Firenze", contact_info="info.firenze@laboratori.it")
        lab_bologna = Laboratory(name="Laboratorio Bologna", address="Via Marconi 12, Bologna", contact_info="info.bologna@laboratori.it")
    
        session.add_all([lab_milano, lab_roma, lab_torino, lab_firenze, lab_bologna])
    
        # Inserimento dei tipi di esame
        esame_sangue = ExamType(name="Esame del Sangue", description="Analisi completa del sangue")
        risonanza = ExamType(name="Risonanza Magnetica", description="Esame di diagnostica per immagini")
        tac = ExamType(name="TAC", description="Tomografia assiale computerizzata")
        ecografia = ExamType(name="Ecografia", description="Esame ecografico generale")
        visita = ExamType(name="Visita Medica", description="Visita specialistica")
    
        session.add_all([esame_sangue, risonanza, tac, ecografia, visita])
    
        # Inserimento delle disponibilità degli operatori
        availability_1 = OperatorsAvailability(
            exam_type_id=1, laboratory_id=1, operator_id=1,
            available_from_date=date(2025, 1, 1), available_to_date=date(2025, 12, 31),
            available_from_time=time(8, 0), available_to_time=time(16, 0),
            available_weekday=1, slot_duration_minutes=30, pause_minutes=10, enabled=True
        )
        availability_2 = OperatorsAvailability(
            exam_type_id=2, laboratory_id=2, operator_id=2,
            available_from_date=date(2025, 1, 1), available_to_date=date(2025, 12, 31),
            available_from_time=time(9, 0), available_to_time=time(17, 0),
            available_weekday=3, slot_duration_minutes=20, pause_minutes=5, enabled=True
        )
        availability_3 = OperatorsAvailability(
            exam_type_id=3, laboratory_id=3, operator_id=3,
            available_from_date=date(2025, 1, 1), available_to_date=date(2025, 12, 31),
            available_from_time=time(10, 0), available_to_time=time(18, 0),
            available_weekday=5, slot_duration_minutes=40, pause_minutes=15, enabled=True
        )
    
        session.add_all([availability_1, availability_2, availability_3])
    
        # Inserimento delle chiusure dei laboratori
        closure_1 = LaboratoryClosure(
            laboratory_id=1, start_datetime=datetime(2025, 8, 1, 8, 0), end_datetime=datetime(2025, 8, 15, 18, 0)
        )
        closure_2 = LaboratoryClosure(
            laboratory_id=2, start_datetime=datetime(2025, 12, 24, 8, 0), end_datetime=datetime(2025, 12, 26, 18, 0)
        )
        closure_3 = LaboratoryClosure(
            laboratory_id=3, start_datetime=datetime(2025, 1, 6, 8, 0), end_datetime=datetime(2025, 1, 6, 18, 0)
        )
    
        session.add_all([closure_1, closure_2, closure_3])
    
        # Commit delle modifiche
        session.commit()

    except IntegrityError as e:
        
        session.rollback()
        print(f"Errore di integrità rilevato: {e}")



    