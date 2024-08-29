#!/bin/bash

### START BLOCKCHAIN ###
nonodo > nonodo.logs & sleep 2

### DEPLOY MUFF TOKEN ###
forge create --rpc-url 127.0.0.1:8545 \
     --constructor-args 100 \
     --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
     erc20/Muff.sol:MUFFToken
sleep 2

### START DAPP ###
rm src/moveuff.db
ROLLUP_HTTP_SERVER_URL="http://127.0.0.1:5004" python3 src/main.py & sleep 2

# ### SEND A TRIP TO DAPP ###
python3 front-end/addInputs.py
sleep 10

### SEND MUFF TO DAPP ###
python3 front-end/portal.py
sleep 5

### STOP ###
# ./stop.sh