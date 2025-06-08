from pydantic import BaseModel
from typing import Optional, List
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
    pseudonimo_cluster: Optional[str] = None
    credibilidade_score: Optional[float] = None

    class Config:
        from_attributes = True


class DenunciaStatusUpdate(BaseModel):
    status: StatusDenuncia


class PseudonymAnalysis(BaseModel):
    """Análise de credibilidade de um pseudônimo (totalmente anônimo)"""
    pseudonimo: str
    total_denuncias: int
    denuncias_verificadas: int
    denuncias_rejeitadas: int
    denuncias_pendentes: int
    taxa_veracidade: float
    credibilidade_score: float
    categorias_frequentes: List[str]
    regioes_frequentes: List[dict]
    primeiro_relato: Optional[str]
    ultimo_relato: Optional[str]
    dias_atividade: int


class SystemMetrics(BaseModel):
    """Métricas de credibilidade do sistema (sem dados pessoais)"""
    pseudonimos_ativos: int
    total_denuncias: int
    taxa_verificacao_geral: float
    pseudonimos_alta_credibilidade: int
    pseudonimos_baixa_credibilidade: int
    categorias_mais_reportadas: List[dict]
    distribuicao_credibilidade: dict


class UserSelfCredibility(BaseModel):
    """Schema para usuário ver sua própria credibilidade (sem revelar pseudônimo)"""
    credibilidade_score: float
    total_denuncias: int
    denuncias_verificadas: int
    denuncias_rejeitadas: int
    denuncias_pendentes: int
    taxa_veracidade: float
    dias_atividade: int
    categorias_frequentes: List[str]
    interpretacao: str
    dica: str