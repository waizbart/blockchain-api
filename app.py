from flask import Flask, request, jsonify
from web3 import Web3
import json

app = Flask(__name__)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

with open("./contracts/report_abi.json") as f:
    contract_abi = json.load(f)
    
contract_address = "0x..."
contract = w3.eth.contract(address=contract_address, abi=contract_abi)
sender_account = w3.eth.accounts[0]
private_key = "0xf18cd1e9c669495964e3cbc030437ec79fa2540a58070cc1e81892d24711b341"

@app.route("/report", methods=["POST"])
def create_report():
    data = request.get_json()
    report_content = data.get("content")

    ipfs_hash = data.get("hash")

    txn = contract.functions.addReport(ipfs_hash).buildTransaction({
        'from': sender_account,
        'nonce': w3.eth.get_transaction_count(sender_account),
        'gas': 3000000,
        'gasPrice': w3.toWei('5', 'gwei')
    })
    
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return jsonify({"status": "ok", "transactionHash": receipt.transactionHash.hex()})

if __name__ == "__main__":
    app.run(debug=True)
