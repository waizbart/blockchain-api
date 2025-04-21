from abc import ABC, abstractmethod
from typing import Any, Optional


class StorageAdapter(ABC):
    """
    Abstract base class for storage adapters.
    """

    @abstractmethod
    def store(self, data: Any) -> str:
        """
        Store data and return an identifier.

        Args:
            data: The data to store.

        Returns:
            A string identifier for the stored data.
        """
        pass

    @abstractmethod
    def retrieve(self, identifier: str) -> Optional[Any]:
        """
        Retrieve data by its identifier.

        Args:
            identifier: The identifier of the data to retrieve.

        Returns:
            The retrieved data, or None if not found.
        """
        pass
