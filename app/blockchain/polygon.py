from web3 import Web3
import json
import os
from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ABI_PATH = os.path.join(BASE_DIR, "contracts", "report_abi.json")
with open(ABI_PATH, "r") as f:
    ABI_CONTRATO = json.load(f)

w3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC))
contract = w3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=ABI_CONTRATO)

def registrar_denuncia(hash_dados: str, categoria: str) -> str:
    """
    Envia transação para registrar denúncia na blockchain
    Retorna o tx_hash.
    """
    nonce = w3.eth.get_transaction_count(settings.PUBLIC_ADDRESS)

    txn = contract.functions.registrarDenuncia(hash_dados, categoria).build_transaction({
        'nonce': nonce,
        'gas': 300000,
        'maxPriorityFeePerGas': w3.to_wei('25', 'gwei'),  
        'maxFeePerGas': w3.to_wei('50', 'gwei'),  
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=settings.PRIVATE_KEY)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    return w3.to_hex(tx_hash)

def obter_total_denuncias() -> int:
    return contract.functions.obterTotalDenuncias().call()

def obter_denuncia(id_denuncia: int):
    return contract.functions.obterDenuncia(id_denuncia).call()
