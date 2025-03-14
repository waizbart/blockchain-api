from fastapi import APIRouter, HTTPException
import hashlib
from app.schemas.denuncia import Denuncia
from app.blockchain.polygon import registrar_denuncia, obter_total_denuncias, obter_denuncia

router = APIRouter()

@router.post("/denuncia")
def criar_denuncia(denuncia: Denuncia):
    """
    Registra uma nova denúncia:
    1. Gera um hash dos dados.
    2. Envia o hash na blockchain via registrarDenuncia().
    """
    try:

        dados_concatenados = f"{denuncia.descricao}{denuncia.categoria}"
        if denuncia.latitude and denuncia.longitude:
            dados_concatenados += f"{denuncia.latitude}{denuncia.longitude}"

        hash_dados = hashlib.sha256(dados_concatenados.encode()).hexdigest()

        tx_hash = registrar_denuncia(hash_dados, denuncia.categoria)

        return {
            "status": "sucesso",
            "tx_hash": tx_hash,
            "hash_dados": hash_dados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/denuncias")
def listar_denuncias():
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
        lista = []
        for i in range(total):
            dado = obter_denuncia(i) 
            lista.append({
                "id": i,
                "hashDados": dado[0],
                "dataHora": dado[1],
                "categoria": dado[2],
            })
        return lista
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
