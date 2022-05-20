# install: pip3 install py-solc-x
# install: pip3 install web3
# install: pip3 install python-dotenv
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

install_solc('0.6.0')

load_dotenv()

with open("./SimpleStorage.sol","r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard (
    {
        "language": "Solidity",
        "sources":{"SimpleStorage.sol":{"content": simple_storage_file}},
        "settings":{
            "outputSelection":{
                "*":{
                    "*":["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.6.0",
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol, file)

# get the bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get the ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# ganache -> simula a blockchain
# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x4E6041E1D06E9B5C7B2DB0e693a9F8D14F9583b3"
private_key = os.getenv("PRIVITE_KEY")

# creating de Contract
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latestest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": my_address, "nonce": nonce}) 
sign_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# send a transaction
tx_hash = w3.eth.send_raw_transaction(sign_txn.rawTransaction)

# wait for transaction be mined
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

#print(tx_receipt)


# interact with a contract

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId":chain_id, "gasPrice": w3.eth.gas_price, "from":my_address, "nonce": nonce + 1
})

signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
