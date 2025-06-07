from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.repositories.denuncia import DenunciaRepository
from app.services.blockchain_service import BlockchainService
from app.schemas.denuncia import Denuncia as DenunciaSchema
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
        # Convert pydantic model to dict for hash generation
        denuncia_dict = denuncia.dict()

        # Generate hash
        hash_dados = self.blockchain_service.generate_hash(denuncia_dict)

        # Register on blockchain
        tx_hash = self.blockchain_service.register_denuncia(
            hash_dados, denuncia.categoria)

        # Store in database
        db_denuncia = self.repository.create_from_schema(denuncia, hash_dados)

        # Store additional data on IPFS if enabled
        ipfs_cid = None
        if self.storage_adapter:
            try:
                # Add more details that might not fit in the blockchain
                additional_data = {
                    "id": db_denuncia.id,
                    "descricao": denuncia.descricao,
                    "categoria": denuncia.categoria,
                    "latitude": denuncia.latitude,
                    "longitude": denuncia.longitude,
                    "datetime": str(denuncia.datetime),
                    "hash_dados": hash_dados,
                    "tx_hash": tx_hash
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

    def get_all_denuncias(self) -> List[Dict[str, Any]]:
        """
        Get all denuncias from blockchain and enrich with database data.
        """
        # Get all denuncias from blockchain
        blockchain_denuncias = self.blockchain_service.get_all_denuncias()

        results = []
        for denuncia_id, hash_dados, data_hora, categoria in blockchain_denuncias:
            # Find corresponding database record
            local_denuncia = self.repository.get_by_hash(hash_dados)

            if local_denuncia:
                results.append({
                    "id": local_denuncia.id,
                    "descricao": local_denuncia.descricao,
                    "categoria": local_denuncia.categoria,
                    "latitude": getattr(local_denuncia, "latitude", None),
                    "longitude": getattr(local_denuncia, "longitude", None),
                    "datetime": local_denuncia.datetime,
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

            # Find in database
            local_denuncia = self.repository.get_by_hash(hash_dados)

            if local_denuncia:
                return {
                    "id": local_denuncia.id,
                    "descricao": local_denuncia.descricao,
                    "categoria": local_denuncia.categoria,
                    "latitude": getattr(local_denuncia, "latitude", None),
                    "longitude": getattr(local_denuncia, "longitude", None),
                    "datetime": local_denuncia.datetime,
                    "blockchain_id": denuncia_id,
                    "blockchain_timestamp": data_hora
                }
            else:
                # Return only blockchain data if no database record found
                return {
                    "blockchain_id": denuncia_id,
                    "hash_dados": hash_dados,
                    "blockchain_timestamp": data_hora,
                    "categoria": categoria
                }
        except Exception as e:
            print(f"Error getting denuncia: {str(e)}")
            return None
