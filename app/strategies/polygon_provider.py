from typing import Tuple, List

from app.blockchain.polygon import w3, contract
from app.core.config import settings
from app.strategies.blockchain_provider import BlockchainProvider


class PolygonProvider(BlockchainProvider):
    """
    Polygon blockchain provider implementation.
    """

    def register_report(self, hash_data: str, category: str) -> str:
        """
        Register a report on the Polygon blockchain.
        """
        nonce = w3.eth.get_transaction_count(settings.PUBLIC_ADDRESS)

        txn = contract.functions.registrarDenuncia(hash_data, category).build_transaction({
            'nonce': nonce,
            'gas': 300000,
            'maxPriorityFeePerGas': w3.to_wei('25', 'gwei'),
            'maxFeePerGas': w3.to_wei('50', 'gwei'),
        })

        signed_txn = w3.eth.account.sign_transaction(
            txn, private_key=settings.PRIVATE_KEY)

        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        return w3.to_hex(tx_hash)

    def get_total_reports(self) -> int:
        """
        Get the total number of reports on the Polygon blockchain.
        """
        return contract.functions.obterTotalDenuncias().call()

    def get_report(self, report_id: int) -> Tuple[str, int, str]:
        """
        Get a report from the Polygon blockchain by ID.
        """
        return contract.functions.obterDenuncia(report_id).call()

    def get_all_reports(self) -> List[Tuple[int, str, int, str]]:
        """
        Get all reports from the Polygon blockchain.
        """
        total = self.get_total_reports()
        reports = []

        print(f"Total de denuncias: {total}")

        START = 20

        for i in range(START, total):
            data = self.get_report(i)
            reports.append((i, data[0], data[1], data[2]))

        return reports
