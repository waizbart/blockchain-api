from fastapi import APIRouter, Depends, HTTPException, Request
from app.db.config import SessionLocal

from app.schemas.denuncia import Denuncia
from app.core.deps import get_current_active_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.services.denuncia_service import DenunciaService
from app.utils.rate_limiter import limiter
from app.core.deps import get_db

router = APIRouter()


@router.get("/")
def hello_world():
    """
    Returns a simple Hello, World! message.
    """
    return {"message": "Hello, World!"}


@router.post("/denuncia")
@limiter.limit("5/minute")
def criar_denuncia(
    request: Request,
    denuncia: Denuncia,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Registra uma nova denúncia:
    1. Gera um hash dos dados.
    2. Envia o hash na blockchain via registrarDenuncia().

    Requer autenticação de usuário.
    """
    try:
        service = DenunciaService(db)
        result = service.create_denuncia(denuncia, current_user.id)

        print(
            f"denuncia {denuncia.datetime} registrada com sucesso na blockchain por usuário {current_user.username}. tx_hash: {result['tx_hash']}")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minha-credibilidade-anonima")
def obter_minha_credibilidade_anonima(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Permite que usuários vejam sua própria credibilidade baseada no pseudônimo.
    Não revela o pseudônimo ao usuário.
    """
    try:
        service = DenunciaService(db)

        pseudonimo = service.clustering_service.generate_anonymous_pseudonym(
            current_user.id)

        analysis = service.clustering_service.get_pseudonym_analysis(
            pseudonimo)

        if analysis is None:
            return {
                "message": "Você ainda não fez denúncias suficientes para calcular credibilidade.",
                "credibilidade_score": 0.5,
                "denuncias_realizadas": 0
            }

        return {
            "credibilidade_score": analysis.credibilidade_score,
            "total_denuncias": analysis.total_denuncias,
            "denuncias_verificadas": analysis.denuncias_verificadas,
            "denuncias_rejeitadas": analysis.denuncias_rejeitadas,
            "denuncias_pendentes": analysis.denuncias_pendentes,
            "taxa_veracidade": analysis.taxa_veracidade,
            "dias_atividade": analysis.dias_atividade,
            "categorias_frequentes": analysis.categorias_frequentes,
            "interpretacao": (
                "Alta credibilidade" if analysis.credibilidade_score >= 0.7 else
                "Credibilidade moderada" if analysis.credibilidade_score >= 0.4 else
                "Baixa credibilidade"
            ),
            "dica": (
                "Excelente! Continue fazendo denúncias precisas!" if analysis.credibilidade_score >= 0.7 else
                "Bom trabalho! Certifique-se de verificar suas informações antes de denunciar." if analysis.credibilidade_score >= 0.4 else
                "Suas denúncias precisam ser mais precisas. Verifique cuidadosamente os dados antes de enviar."
            ),
            "observacao": "Seus dados permanecem completamente anônimos. Este score é baseado em padrões agregados."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
