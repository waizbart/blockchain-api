from pydantic import BaseModel
from typing import Optional
from app.models.denuncia import StatusDenuncia, SeveridadeDenuncia


class Denuncia(BaseModel):
    descricao: str
    categoria: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    datetime: Optional[str] = None
    user_uuid: Optional[str] = None


class DenunciaResponse(BaseModel):
    id: int
    descricao: str
    categoria: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    datetime: Optional[str] = None
    status: StatusDenuncia
    hash_dados: str
    user_uuid: Optional[str] = None
    severidade: Optional[SeveridadeDenuncia] = None

    class Config:
        orm_mode = True


class DenunciaStatusUpdate(BaseModel):
    status: StatusDenuncia


class SeveridadeAnalysis(BaseModel):
    severidade: SeveridadeDenuncia
    pontuacao: float
    fatores: dict
    justificativa: str
