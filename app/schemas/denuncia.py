from pydantic import BaseModel
from typing import Optional

class Denuncia(BaseModel):
    descricao: str
    categoria: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
