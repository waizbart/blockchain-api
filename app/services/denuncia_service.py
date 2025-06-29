from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.repositories.denuncia import DenunciaRepository
from app.services.blockchain_service import BlockchainService
from app.schemas.denuncia import Denuncia as DenunciaSchema
from app.models.denuncia import StatusDenuncia, SeveridadeDenuncia
from app.adapters.storage_adapter import StorageAdapter
from app.adapters.ipfs_adapter import IPFSAdapter


class DenunciaService:
    """
    Service for managing denuncias, combining blockchain and database operations.
    """

    def __init__(self, db: Session, blockchain_provider: str = "polygon", use_ipfs: bool = False):
        """
        Initialize the denuncia service.

        Args:
            db: Database session.
            blockchain_provider: The blockchain provider to use.
            use_ipfs: Whether to use IPFS for additional storage.
        """
        self.repository = DenunciaRepository(db)
        self.blockchain_service = BlockchainService(
            provider_name=blockchain_provider)
        self.storage_adapter: Optional[StorageAdapter] = None

        if use_ipfs:
            try:
                self.storage_adapter = IPFSAdapter()
            except Exception as e:
                print(f"IPFS not available: {str(e)}")

    def create_denuncia(self, denuncia: DenunciaSchema) -> Dict[str, Any]:
        """
        Create a new denuncia:
        1. Generate hash from denuncia data
        2. Register hash on blockchain
        3. Store denuncia in database
        4. If IPFS is enabled, store additional data on IPFS
        """
        denuncia_dict = denuncia.dict()
        hash_dados = self.blockchain_service.generate_hash(denuncia_dict)
        tx_hash = self.blockchain_service.register_denuncia(
            hash_dados, denuncia.categoria)
        db_denuncia = self.repository.create_from_schema(denuncia, hash_dados)

        try:
            from app.services.severity_analysis_service import SeverityAnalysisService
            severity_service = SeverityAnalysisService(self.repository.db)
            analysis = severity_service.analyze_severity(db_denuncia)

            db_denuncia.severidade = analysis['severidade']
            self.repository.db.commit()
            self.repository.db.refresh(db_denuncia)
        except Exception as e:
            print(f"Erro na análise de severidade: {str(e)}")

        ipfs_cid = None
        if self.storage_adapter:
            try:
                additional_data = {
                    "id": db_denuncia.id,
                    "descricao": denuncia.descricao,
                    "categoria": denuncia.categoria,
                    "latitude": denuncia.latitude,
                    "longitude": denuncia.longitude,
                    "datetime": str(denuncia.datetime),
                    "hash_dados": hash_dados,
                    "tx_hash": tx_hash,
                    "status": db_denuncia.status.value
                }

                ipfs_cid = self.storage_adapter.store(additional_data)
            except Exception as e:
                print(f"Failed to store data on IPFS: {str(e)}")

        response = {
            "status": "sucesso",
            "tx_hash": tx_hash,
            "hash_dados": hash_dados
        }

        if ipfs_cid:
            response["ipfs_cid"] = ipfs_cid

        return response

    def update_denuncia_status(self, denuncia_id: int, new_status: StatusDenuncia) -> Optional[Dict[str, Any]]:
        """
        Update the status of a denuncia. Only allows certain transitions.
        """
        denuncia = self.repository.update_status(denuncia_id, new_status)

        if denuncia:
            return {
                "id": denuncia.id,
                "descricao": denuncia.descricao,
                "categoria": denuncia.categoria,
                "latitude": denuncia.latitude,
                "longitude": denuncia.longitude,
                "datetime": denuncia.datetime,
                "status": denuncia.status.value,
                "hash_dados": denuncia.hash_dados,
                "user_uuid": denuncia.user_uuid,
                "severidade": denuncia.severidade.value if denuncia.severidade else None
            }
        return None

    def get_all_denuncias(
        self,
        status: Optional[StatusDenuncia] = None,
        categoria: Optional[str] = None,
        blockchain_offset: Optional[int] = 0,
        user_uuid: Optional[str] = None,
        severidade: Optional[SeveridadeDenuncia] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all denuncias from blockchain and enrich with database data.
        Supports filtering by status, categoria, user_uuid, and severidade.
        """
        blockchain_denuncias = self.blockchain_service.get_all_denuncias(
            blockchain_offset)

        results = []
        for denuncia_id, hash_dados, data_hora, categoria_blockchain in blockchain_denuncias:
            local_denuncia = self.repository.get_by_hash(hash_dados)

            if local_denuncia:
                if status and local_denuncia.status != status:
                    continue

                if categoria and local_denuncia.categoria.lower() != categoria.lower():
                    continue

                if user_uuid and local_denuncia.user_uuid != user_uuid:
                    continue

                if severidade and local_denuncia.severidade != severidade:
                    continue

                results.append({
                    "id": local_denuncia.id,
                    "descricao": local_denuncia.descricao,
                    "categoria": local_denuncia.categoria,
                    "latitude": getattr(local_denuncia, "latitude", None),
                    "longitude": getattr(local_denuncia, "longitude", None),
                    "datetime": local_denuncia.datetime,
                    "status": local_denuncia.status.value,
                    "hash_dados": local_denuncia.hash_dados,
                    "user_uuid": getattr(local_denuncia, "user_uuid", None),
                    "severidade": local_denuncia.severidade.value if local_denuncia.severidade else None,
                    "blockchain_id": denuncia_id,
                    "blockchain_timestamp": data_hora
                })

        return results

    def get_denuncia_by_blockchain_id(self, denuncia_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific denuncia by its blockchain ID.
        """
        try:
            total = self.blockchain_service.get_total_denuncias()
            if denuncia_id < 0 or denuncia_id >= total:
                return None

            hash_dados, data_hora, categoria = self.blockchain_service.get_denuncia(
                denuncia_id)

            local_denuncia = self.repository.get_by_hash(hash_dados)

            if local_denuncia:
                return {
                    "id": local_denuncia.id,
                    "descricao": local_denuncia.descricao,
                    "categoria": local_denuncia.categoria,
                    "latitude": getattr(local_denuncia, "latitude", None),
                    "longitude": getattr(local_denuncia, "longitude", None),
                    "datetime": local_denuncia.datetime,
                    "status": local_denuncia.status.value,
                    "hash_dados": local_denuncia.hash_dados,
                    "user_uuid": getattr(local_denuncia, "user_uuid", None),
                    "severidade": local_denuncia.severidade.value if local_denuncia.severidade else None,
                    "blockchain_id": denuncia_id,
                    "blockchain_timestamp": data_hora
                }
            else:
                return {
                    "blockchain_id": denuncia_id,
                    "hash_dados": hash_dados,
                    "blockchain_timestamp": data_hora,
                    "categoria": categoria
                }
        except Exception as e:
            print(f"Error getting denuncia: {str(e)}")
            return None
