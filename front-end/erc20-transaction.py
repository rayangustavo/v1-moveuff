from web3 import Web3
import json
import time
import rsa

anvil = "http://localhost:8545"
web3 = Web3(Web3.HTTPProvider(anvil))

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

muff_address = "0x59b670e9fa9d0a427751af201d676719a970857b"
muff_checksum_address = Web3.to_checksum_address(muff_address)
with open("./front-end/abi-contracts/MUFF.json", "r") as abi:
    muff_ABI = json.load(abi)

muff_contract = web3.eth.contract(abi=muff_ABI, address=muff_checksum_address)

from_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
from_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
to_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"

gas = web3.eth.gas_price
nonce = web3.eth.get_transaction_count(from_address)
tx = muff_contract.functions.transfer(to_address, 10).build_transaction({'from':from_address, 'nonce':nonce, 'gasPrice': gas})
signed_tx = web3.eth.account.sign_transaction(tx, private_key=from_private_key)
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction).hex()
# web3.wait_for_transaction_receipt(tx_hash)
to_balance = muff_contract.functions.balanceOf(to_address).call()
print(tx_hash, "\n", to_balance)
