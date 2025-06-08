from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from app.db.config import SessionLocal
from app.models.denuncia import StatusDenuncia
from app.schemas.denuncia import DenunciaStatusUpdate, PseudonymAnalysis, SystemMetrics
from app.core.deps import get_current_admin, get_db
from app.models.user import User
from sqlalchemy.orm import Session
from app.services.denuncia_service import DenunciaService
from app.services.blockchain_service import BlockchainService

router = APIRouter()


def get_blockchain_service() -> BlockchainService:
    return BlockchainService()


@router.get("/denuncias")
def listar_denuncias(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    status: Optional[StatusDenuncia] = None,
    categoria: Optional[str] = None,
    blockchain_offset: Optional[int] = 0,
):
    """
    Retorna todas as denúncias armazenadas no contrato.
    Requer privilégios de administrador.
    """
    try:
        service = DenunciaService(db)
        results = service.get_all_denuncias(
            status, categoria, blockchain_offset)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/denuncias/{denuncia_id}/status")
def atualizar_status_denuncia(
    denuncia_id: int,
    status_update: DenunciaStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Atualiza o status de uma denúncia.
    Apenas administradores podem alterar o status.
    """
    try:
        service = DenunciaService(db)
        result = service.update_denuncia_status(
            denuncia_id, status_update.status)

        if result is None:
            raise HTTPException(
                status_code=404, detail="Denúncia não encontrada.")

        return {
            "message": f"Status da denúncia {denuncia_id} atualizado para {status_update.status.value}",
            "denuncia": result
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/denuncias/{denuncia_id}")
def obter_denuncia_por_id(
    denuncia_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin)
):
    """
    Retorna uma denúncia específica pelo ID salvo na blockchain.
    Requer privilégios de administrador.
    """
    try:
        service = DenunciaService(db)
        denuncia = service.get_denuncia_by_blockchain_id(denuncia_id)

        if denuncia is None:
            raise HTTPException(
                status_code=404, detail="Denúncia não encontrada.")

        return denuncia
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clustering/metricas", response_model=SystemMetrics)
def obter_metricas_sistema(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas do sistema de clustering anônimo.
    Apenas para administradores. Não expõe dados pessoais.
    """
    try:
        service = DenunciaService(db)
        metrics = service.clustering_service.get_system_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clustering/pseudonimos-baixa-credibilidade", response_model=List[PseudonymAnalysis])
def listar_pseudonimos_baixa_credibilidade(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    threshold: float = 0.3,
    min_reports: int = 3
):
    """
    Lista pseudônimos com baixa credibilidade.
    Útil para identificar padrões suspeitos mantendo anonimato.
    """
    try:
        service = DenunciaService(db)
        pseudonyms = service.clustering_service.get_low_credibility_pseudonyms(
            threshold, min_reports)
        return pseudonyms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clustering/pseudonimos-alta-credibilidade", response_model=List[PseudonymAnalysis])
def listar_pseudonimos_alta_credibilidade(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    threshold: float = 0.7,
    min_reports: int = 3
):
    """
    Lista pseudônimos com alta credibilidade.
    Identifica padrões de reportadores confiáveis.
    """
    try:
        service = DenunciaService(db)
        pseudonyms = service.clustering_service.get_high_credibility_pseudonyms(
            threshold, min_reports)
        return pseudonyms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clustering/pseudonimo/{pseudonimo}", response_model=PseudonymAnalysis)
def obter_analise_pseudonimo(
    pseudonimo: str,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Retorna análise detalhada de um pseudônimo específico.
    Mantém anonimato completo.
    """
    try:
        service = DenunciaService(db)
        analysis = service.clustering_service.get_pseudonym_analysis(
            pseudonimo)

        if analysis is None:
            raise HTTPException(
                status_code=404, detail="Pseudônimo não encontrado ou sem denúncias suficientes.")

        return analysis
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/denuncias/com-pseudonimos")
def listar_denuncias_com_pseudonimos(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """
    Lista denúncias com informações de pseudônimos e credibilidade.
    Mantém anonimato total - não expõe dados pessoais.
    """
    try:
        service = DenunciaService(db)
        denuncias = service.clustering_service.get_denuncias_with_credibility(
            limit)
        return {
            "denuncias": denuncias,
            "total": len(denuncias),
            "observacao": "Pseudônimos são completamente anônimos e irreversíveis"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def get_system_status(
    _: User = Depends(get_current_admin),
    blockchain_service: BlockchainService = Depends(get_blockchain_service)
):
    """
    Returns the status of the blockchain account, including balance and
    estimated number of remaining reports.
    Only accessible by admin users.
    """
    try:
        balance = blockchain_service.get_balance()
        cost_per_report = blockchain_service.estimate_report_cost()

        if cost_per_report > 0:
            remaining_reports = int(balance / cost_per_report)
        else:
            remaining_reports = float('inf')

        return {
            "account_balance_matic": balance,
            "estimated_cost_per_report_matic": cost_per_report,
            "estimated_remaining_reports": remaining_reports
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
