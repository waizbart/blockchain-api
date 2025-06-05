from abc import ABC, abstractmethod
from typing import Tuple, Any, List


class BlockchainProvider(ABC):
    """
    Abstract base class for blockchain providers.
    Defines the strategy interface for interacting with different blockchains.
    """

    @abstractmethod
    def register_report(self, hash_data: str, category: str) -> str:
        """
        Register a report on the blockchain.

        Args:
            hash_data: The hash of the report data.
            category: The category of the report.

        Returns:
            The transaction hash.
        """
        pass

    @abstractmethod
    def get_total_reports(self) -> int:
        """
        Get the total number of reports on the blockchain.

        Returns:
            The total number of reports.
        """
        pass

    @abstractmethod
    def get_report(self, report_id: int) -> Tuple[str, int, str]:
        """
        Get a report from the blockchain by ID.

        Args:
            report_id: The ID of the report to get.

        Returns:
            A tuple of (hash_data, timestamp, category).
        """
        pass

    @abstractmethod
    def get_all_reports(self) -> List[Tuple[int, str, int, str]]:
        """
        Get all reports from the blockchain.

        Returns:
            A list of tuples (id, hash_data, timestamp, category).
        """
        pass

    @abstractmethod
    def get_balance(self) -> float:
        """
        Get the balance of the blockchain account.

        Returns:
            The balance in the native currency (e.g., ETH, MATIC).
        """
        pass

    @abstractmethod
    def estimate_report_cost(self) -> float:
        """
        Estimate the cost of a single report registration transaction.

        Returns:
            The estimated cost in the native currency.
        """
        pass
