from typing import Dict, Type

from app.blockchain.polygon import w3 as polygon_w3
from app.strategies.blockchain_provider import BlockchainProvider
from app.strategies.polygon_provider import PolygonProvider


class BlockchainFactory:
    """
    Factory for creating blockchain provider instances.
    """
    _providers: Dict[str, Type[BlockchainProvider]] = {
        "polygon": PolygonProvider
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> BlockchainProvider:
        """
        Get a blockchain provider by name.

        Args:
            provider_name: The name of the provider to get.

        Returns:
            An instance of the requested provider.

        Raises:
            ValueError: If the provider name is not supported.
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(
                f"Unsupported blockchain provider: {provider_name}")

        return provider_class()
