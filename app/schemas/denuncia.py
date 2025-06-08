from pydantic import BaseModel
from typing import Optional
from app.models.denuncia import StatusDenuncia


class Denuncia(BaseModel):
    descricao: str
    categoria: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    datetime: Optional[str] = None


class DenunciaResponse(BaseModel):
    id: int
    descricao: str
    categoria: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    datetime: Optional[str] = None
    status: StatusDenuncia
    hash_dados: str

    class Config:
        orm_mode = True


class DenunciaStatusUpdate(BaseModel):
    status: StatusDenuncia
