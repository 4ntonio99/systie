from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from src.shared.database import Base

class UserModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    curp = Column(String(18), unique=True, nullable=False, index=True)
    rfc = Column(String(13), unique=True, nullable=False, index=True)
    adsc = Column(String(50), nullable=False)
    nivel = Column(String(50), nullable=False, default="usuario")

class AttendanceModel(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    curp = Column(String(18), index=True, nullable=False)
    fecha = Column(String(20), nullable=False)
    horario_e1 = Column(String(10), nullable=True)
    reg_e1 = Column(String(10), nullable=True)
    edo_e1 = Column(String(10), nullable=True)
    horario_s1 = Column(String(10), nullable=True)
    reg_s1 = Column(String(10), nullable=True)
    edo_s1 = Column(String(10), nullable=True)
    reg_s2 = Column(String(10), nullable=True)

class HorariosModel(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    curp = Column(String(18), index=True, nullable=False)
    entrada = Column(String(10), nullable=True)
    salida = Column(String(10), nullable=True)