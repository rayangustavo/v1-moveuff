from web3 import Web3
import json
import time
import rsa

anvil = "http://localhost:8545"
web3 = Web3(Web3.HTTPProvider(anvil))

def str2hex(str):
    return "0x" + str.encode("utf-8").hex()

inputBox_address = "0x59b22D57D4f067708AB0c00552767405926dc768"
with open("./front-end/abi-contracts/InputBox.json", "r") as abi:
    inputBox_ABI = json.load(abi)
inputBox_contract = web3.eth.contract(abi=inputBox_ABI, address=inputBox_address)

tempo = time.time()
dict_input = {"id_bike": 1, "id_user": 1, "source_parking_station": 1, "destination_parking_station": 2, 
              "source_timestamp": tempo, "destination_timestamp": tempo + 1000, "travelled_distance": 3000}

wallet_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
dapp_address = "0xab7528bb862fB57E8A2BCd567a2e929a0Be56a5e"

input = Web3.to_bytes(hexstr=str2hex(json.dumps(dict_input)))
gas = web3.eth.gas_price
nonce = web3.eth.get_transaction_count(wallet_address)
tx = inputBox_contract.functions.addInput(dapp_address, input).build_transaction({'from':wallet_address, 'nonce':nonce, 'gasPrice': gas})
signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction).hex()

print(tx_hash)