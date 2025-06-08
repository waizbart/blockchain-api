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

    def get_all_reports(self, blockchain_offset: int = 0) -> List[Tuple[int, str, int, str]]:
        """
        Get all reports from the Polygon blockchain.
        """
        total = self.get_total_reports()
        reports = []

        print(f"Total de denuncias: {total}")

        for i in range(blockchain_offset, total):
            data = self.get_report(i)
            reports.append((i, data[0], data[1], data[2]))

        return reports

    def get_balance(self) -> float:
        """
        Get the balance of the configured public address.
        """
        balance_wei = w3.eth.get_balance(settings.PUBLIC_ADDRESS)
        balance_matic = w3.from_wei(balance_wei, 'ether')
        return float(balance_matic)

    def estimate_report_cost(self) -> float:
        """
        Estimate the cost of a single 'registrarDenuncia' transaction.
        """
        try:
            dummy_hash = "0x" + "0" * 64
            dummy_category = "estimativa"

            gas_estimate = contract.functions.registrarDenuncia(dummy_hash, dummy_category).estimate_gas({
                'from': settings.PUBLIC_ADDRESS
            })

            gas_price = w3.eth.gas_price

            cost_wei = gas_estimate * gas_price
            cost_matic = w3.from_wei(cost_wei, 'ether')

            return float(cost_matic)
        except Exception as e:
            print(f"Error estimating gas: {e}")
            return 0.01
