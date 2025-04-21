from fastapi import APIRouter, Depends, HTTPException
import hashlib
from app.db.config import SessionLocal
from app.schemas.denuncia import Denuncia
from app.models.denuncia import Denuncia as DenunciaModel
from app.blockchain.polygon import registrar_denuncia, obter_total_denuncias, obter_denuncia
from app.controllers.police import get_current_police, Police
from sqlalchemy.orm import Session

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
        dados_concatenados = f"{denuncia.descricao}{denuncia.categoria}{denuncia.datetime}"
        if denuncia.latitude and denuncia.longitude:
            dados_concatenados += f"{denuncia.latitude}{denuncia.longitude}"

        hash_dados = hashlib.sha256(dados_concatenados.encode()).hexdigest()

        tx_hash = registrar_denuncia(hash_dados, denuncia.categoria)

        print(f"denuncia {denuncia.datetime} registrada com sucesso na blockchain. tx_hash: {tx_hash}")
        
        nova_denuncia = DenunciaModel(
            descricao=denuncia.descricao,
            categoria=denuncia.categoria,
            latitude=denuncia.latitude, 
            longitude=denuncia.longitude,
            hash_dados=hash_dados,
            datetime=denuncia.datetime
        )
        db.add(nova_denuncia)
        db.commit()
        db.refresh(nova_denuncia)

        return {
            "status": "sucesso",
            "tx_hash": tx_hash,
            "hash_dados": hash_dados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/denuncias")
def listar_denuncias(
    current_police: Police = Depends(get_current_police),
    db: Session = Depends(get_db)
):
    """
    Retorna todas as denúncias armazenadas no contrato.
    Para cada denúncia, a estrutura é:
    {
      "id": ...,
      "hashDados": ...,
      "dataHora": ...,
      "categoria": ...
    }
    """
    try:
        total = obter_total_denuncias()
        results = []
        for i in range(total):
            data = obter_denuncia(i) 
            
            local_denuncia = db.query(DenunciaModel).filter_by(hash_dados=data[0]).first()

            if local_denuncia:
                print(f"Denúncia encontrada: {local_denuncia.datetime}")
                results.append({
                    "id": local_denuncia.id,
                    "descricao": local_denuncia.descricao,
                    "categoria": local_denuncia.categoria,
                    "latitude": getattr(local_denuncia, "latitude", None),
                    "longitude": getattr(local_denuncia, "longitude", None),
                    "datetime": local_denuncia.datetime,
                })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/denuncias/{denuncia_id}")
def obter_denuncia_por_id(denuncia_id: int):
    """
    Retorna uma denúncia específica pelo ID salvo na blockchain.
    """
    try:
        total = obter_total_denuncias()
        if denuncia_id < 0 or denuncia_id >= total:
            raise HTTPException(status_code=404, detail="Denúncia não encontrada.")

        dado = obter_denuncia(denuncia_id)
        return {
            "id": denuncia_id,
            "hashDados": dado[0],
            "dataHora": dado[1],
            "categoria": dado[2],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
