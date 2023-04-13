# Run this script from simulation directory

HTTP_ADDR=192.168.5.220
HTTP_PORT=8545

# Pre-simulation stage #########################################################

echo "------------------------------PRE-SIMULATION------------------------------"

rm -rf ./geth/keystore ./geth/geth ./geth/genesis.json &&
echo "[PRE-SIMULATION] Finished removing geth artifacts."

geth --verbosity 1 account new --password ./geth/password.txt --datadir ./geth > /dev/null &&
echo "[PRE-SIMULATION] Finished creating new account."

ACCOUNT_ADDRESS=`python3.10 ./geth/scripts/build-genesis.py` &&
echo "[PRE-SIMULATION] Finished creating genesis.json."

geth --verbosity 1 init --datadir geth ./geth/genesis.json > /dev/null &&
echo "[PRE-SIMULATION] Finished initializing blockchain."

echo "[PRE-SIMULATION] Running geth client..."
geth --datadir ./geth \
     --nat extip:$HTTP_ADDR \
     --networkid 123 \
     --netrestrict $HTTP_ADDR/24 \
     --port 30303 \
     --authrpc.port 8551 \
     --http \
     --http.port $HTTP_PORT \
     --http.api personal,eth,net,web3,admin,txpool \
     --allow-insecure-unlock \
     --mine \
     --miner.gasprice 0 \
     --unlock $ACCOUNT_ADDRESS \
     --password ./geth/password.txt \
     --verbosity 1 &

s=10
echo "[PRE-SIMULATION] Sleep for $s seconds to wait for geth to stabilize..."
sleep $s
echo "[PRE-SIMULATION] Finished sleeping."

contract_address=`python3.10 ./geth/scripts/deploy-contract.py $HTTP_PORT` &&
echo "[PRE-SIMULATION] Finished deploying contract into the blockchain."

echo "------------------------------SIMULATION----------------------------------"


echo "-----------------------------POST-SIMULATION------------------------------"

pid=`ps | grep geth | sed 's@^[^0-9]*\([0-9]\+\).*@\1@'`
kill $pid &&
echo "[POST-SIMULATION] Finished killing geth process"