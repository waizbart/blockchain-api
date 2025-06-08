from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from app.db.config import SessionLocal
from app.models.denuncia import StatusDenuncia
from app.schemas.denuncia import Denuncia, DenunciaStatusUpdate
from app.controllers.police import get_current_police, Police
from sqlalchemy.orm import Session
from app.services.denuncia_service import DenunciaService
from app.utils.rate_limiter import limiter

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def hello_world():
    """
    Returns a simple Hello, World! message.
    """
    return {"message": "Hello, World!"}


@router.post("/denuncia")
@limiter.limit("5/minute")
def criar_denuncia(request: Request, denuncia: Denuncia, db: Session = Depends(get_db)):
    """
    Registra uma nova denúncia:
    1. Gera um hash dos dados.
    2. Envia o hash na blockchain via registrarDenuncia().
    """
    try:
        service = DenunciaService(db)
        result = service.create_denuncia(denuncia)

        print(
            f"denuncia {denuncia.datetime} registrada com sucesso na blockchain. tx_hash: {result['tx_hash']}")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/denuncias")
def listar_denuncias(
    _: Police = Depends(get_current_police),
    db: Session = Depends(get_db),
    status: Optional[StatusDenuncia] = None,
    categoria: Optional[str] = None,
    blockchain_offset: Optional[int] = 0,
):
    """
    Retorna todas as denúncias armazenadas no contrato.
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
    _: Police = Depends(get_current_police),
    db: Session = Depends(get_db)
):
    """
    Atualiza o status de uma denúncia.
    Apenas policiais podem alterar o status.
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
def obter_denuncia_por_id(denuncia_id: int, db: Session = Depends(get_db)):
    """
    Retorna uma denúncia específica pelo ID salvo na blockchain.
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
