from fastapi import APIRouter, Depends, HTTPException
from app.db.config import SessionLocal
from app.schemas.denuncia import Denuncia
from app.controllers.police import get_current_police, Police
from sqlalchemy.orm import Session
from app.services.denuncia_service import DenunciaService

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
def criar_denuncia(denuncia: Denuncia, db: Session = Depends(get_db)):
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
    current_police: Police = Depends(get_current_police),
    db: Session = Depends(get_db)
):
    """
    Retorna todas as denúncias armazenadas no contrato.
    """
    try:
        service = DenunciaService(db)
        results = service.get_all_denuncias()
        return results
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
