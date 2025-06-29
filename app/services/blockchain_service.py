import hashlib
from typing import Dict, Any, List, Tuple

from app.factories.blockchain_factory import BlockchainFactory
from app.strategies.blockchain_provider import BlockchainProvider


class BlockchainService:
    """
    Service for interacting with the blockchain.
    Uses the Strategy Pattern through BlockchainProvider implementations.
    """

    def __init__(self, provider_name: str = "polygon"):
        """
        Initialize the blockchain service with a provider.

        Args:
            provider_name: The name of the blockchain provider to use.
        """
        self.provider: BlockchainProvider = BlockchainFactory.get_provider(
            provider_name)

    @staticmethod
    def generate_hash(denuncia_data: Dict[str, Any]) -> str:
        """
        Generate a hash from denuncia data, including optional user_uuid.
        """
        dados_concatenados = f"{denuncia_data.get('descricao')}{denuncia_data.get('categoria')}{denuncia_data.get('datetime')}"
        if (
            denuncia_data.get('latitude') is not None
            and denuncia_data.get('longitude') is not None
        ):
            dados_concatenados += f"{denuncia_data.get('latitude')}{denuncia_data.get('longitude')}"

        if denuncia_data.get('user_uuid') is not None:
            dados_concatenados += f"{denuncia_data.get('user_uuid')}"

        return hashlib.sha256(dados_concatenados.encode()).hexdigest()

    def register_denuncia(self, hash_dados: str, categoria: str) -> str:
        """
        Register a denuncia on the blockchain.
        Returns the transaction hash.
        """
        return self.provider.register_report(hash_dados, categoria)

    def get_total_denuncias(self) -> int:
        """
        Get the total number of denuncias on the blockchain.
        """
        return self.provider.get_total_reports()

    def get_denuncia(self, denuncia_id: int) -> Tuple[str, int, str]:
        """
        Get a denuncia from the blockchain by ID.
        Returns a tuple of (hashDados, dataHora, categoria).
        """
        return self.provider.get_report(denuncia_id)

    def get_all_denuncias(self, blockchain_offset: int = 0) -> List[Tuple[int, str, int, str]]:
        """
        Get all denuncias from the blockchain.
        Returns a list of tuples (id, hashDados, dataHora, categoria).
        """
        return self.provider.get_all_reports(blockchain_offset)

    def get_balance(self) -> float:
        """
        Get the balance from the provider.
        """
        return self.provider.get_balance()

    def estimate_report_cost(self) -> float:
        """
        Estimate the report cost from the provider.
        """
        return self.provider.estimate_report_cost()
