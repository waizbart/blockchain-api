from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.deps import get_current_admin, get_db
from app.models.user import User
from sqlalchemy.orm import Session
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.get("/reliability/{user_uuid}")
def get_user_reliability(
    user_uuid: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtém a análise de confiabilidade de um usuário específico baseada
    no histórico de status das suas denúncias.

    Requer privilégios de administrador.

    Args:
        user_uuid: UUID do usuário para análise

    Returns:
        Métricas de confiabilidade incluindo:
        - Score de confiabilidade
        - Porcentagem de confiabilidade  
        - Nível de confiabilidade
        - Breakdown por status das denúncias
        - Taxas de verificação e rejeição
    """
    try:
        service = AnalysisService(db)
        result = service.get_user_reliability(user_uuid)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reliability/ranking")
def get_users_reliability_ranking(
    limit: Optional[int] = Query(
        10, ge=1, le=100, description="Número máximo de usuários no ranking"),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtém um ranking dos usuários mais confiáveis baseado no histórico
    de suas denúncias.

    Requer privilégios de administrador.

    Args:
        limit: Número máximo de usuários a retornar (padrão: 10, máx: 100)

    Returns:
        Ranking de usuários ordenado por score de confiabilidade, incluindo:
        - Posição no ranking
        - Score e porcentagem de confiabilidade
        - Número total de denúncias
        - Denúncias verificadas e rejeitadas
    """
    try:
        service = AnalysisService(db)
        result = service.get_users_reliability_ranking(limit)

        # Add ranking position to each user
        for i, user_data in enumerate(result.get("ranking", []), 1):
            user_data["ranking_position"] = i

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
def get_analysis_overview(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas gerais do sistema de denúncias para análise.

    Requer privilégios de administrador.

    Returns:
        Visão geral das estatísticas do sistema incluindo:
        - Total de usuários com denúncias
        - Distribuição por níveis de confiabilidade
        - Estatísticas gerais do sistema
    """
    try:
        service = AnalysisService(db)

        all_users_data = service.get_users_reliability_ranking(limit=None)

        if not all_users_data["ranking"]:
            return {
                "message": "Nenhum dado disponível para análise",
                "total_users": 0,
                "reliability_distribution": {}
            }

        reliability_distribution = {
            "MUITO_CONFIAVEL": 0,
            "CONFIAVEL": 0,
            "MODERADA": 0,
            "BAIXA": 0,
            "MUITO_BAIXA": 0
        }

        total_denuncias = 0
        total_verified = 0
        total_rejected = 0

        for user_data in all_users_data["ranking"]:
            reliability_level = user_data["reliability_level"]
            reliability_distribution[reliability_level] += 1
            total_denuncias += user_data["total_denuncias"]
            total_verified += user_data["verified"]
            total_rejected += user_data["rejected"]

        return {
            "total_users_with_denuncias": all_users_data["total_users"],
            "reliability_distribution": reliability_distribution,
            "system_stats": {
                "total_denuncias": total_denuncias,
                "total_verified": total_verified,
                "total_rejected": total_rejected,
                "global_verification_rate": f"{(total_verified / max(1, total_verified + total_rejected) * 100):.2f}%" if (total_verified + total_rejected) > 0 else "N/A",
                "global_rejection_rate": f"{(total_rejected / max(1, total_verified + total_rejected) * 100):.2f}%" if (total_verified + total_rejected) > 0 else "N/A"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
