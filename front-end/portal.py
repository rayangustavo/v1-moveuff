from web3 import Web3
import json
import time
import rsa

anvil = "http://localhost:8545"
web3 = Web3(Web3.HTTPProvider(anvil))

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

portal_address = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB"
portal_checksum_address = Web3.to_checksum_address(portal_address)
with open("./front-end/abi-contracts/ERC20Portal.json", "r") as abi:
    portal_ABI = json.load(abi)["abi"]
portal_contract = web3.eth.contract(abi=portal_ABI, address=portal_checksum_address)

muff_address = "0x59b670e9fa9d0a427751af201d676719a970857b"
# muff_address = "0x4ed7c70F96B99c776995fB64377f0d4aB3B0e1C1"

muff_checksum_address = Web3.to_checksum_address(muff_address)
with open("./front-end/abi-contracts/MUFF.json", "r") as abi:
    muff_ABI = json.load(abi)

muff_contract = web3.eth.contract(abi=muff_ABI, address=muff_checksum_address)
amount = 10

wallet_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
dapp_address = "0xab7528bb862fB57E8A2BCd567a2e929a0Be56a5e"
# dapp_checksum_address = Web3.to_checksum_address(dapp_address)

extra_data = Web3.to_bytes(text="erc20_deposit")

balance = muff_contract.functions.balanceOf(wallet_address).call()

gas = web3.eth.gas_price

nonce = web3.eth.get_transaction_count(wallet_address)
approve_tx = muff_contract.functions.approve(portal_address, balance).build_transaction({'from':wallet_address, 'gasPrice':gas,'nonce': nonce})
signed_approve_tx = web3.eth.account.sign_transaction(approve_tx, private_key=private_key)
tx_hash = web3.eth.send_raw_transaction(signed_approve_tx.raw_transaction).hex()
web3.eth.wait_for_transaction_receipt(tx_hash)

nonce = web3.eth.get_transaction_count(wallet_address)
tx = portal_contract.functions.depositERC20Tokens(muff_checksum_address, dapp_address, amount, extra_data).build_transaction({'from':wallet_address, 'nonce':nonce, 'gasPrice': gas})
signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction).hex()

balance = muff_contract.functions.balanceOf(wallet_address).call()