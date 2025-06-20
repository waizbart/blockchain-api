from sqlalchemy import Column, Integer, String, Text, Float, Enum
from app.db.config import Base
import enum


class StatusDenuncia(enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class SeveridadeDenuncia(enum.Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class Denuncia(Base):
    __tablename__ = "denuncias"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    datetime = Column(String, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    hash_dados = Column(Text, nullable=False)
    user_uuid = Column(String, nullable=True, index=True)
    status = Column(Enum(StatusDenuncia),
                    default=StatusDenuncia.PENDING, nullable=False)
    severidade = Column(Enum(SeveridadeDenuncia), nullable=True)
