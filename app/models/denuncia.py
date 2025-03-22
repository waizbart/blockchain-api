from sqlalchemy import Column, Integer, String, Text, Float
from app.db.config import Base

class Denuncia(Base):
    __tablename__ = "denuncias"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    hash_dados = Column(Text, nullable=False)