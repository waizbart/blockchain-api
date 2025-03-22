from sqlalchemy import Column, Integer, String
from app.db.config import Base

class Police(Base):
    __tablename__ = "police"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)