current_dir=${PWD##*/}

if [ "$current_dir" != "simulation" ]; then
     echo "Error: Current directory must be simulation before running this script!"
     exit 1
fi

ip_addr=192.168.5.220
http_port=8545

echo "------------------------------PRE-SIMULATION------------------------------"

rm -rf ./geth/keystore ./geth/geth ./geth/genesis.json &&
echo "[PRE-SIMULATION] Finished removing geth artifacts."

geth --verbosity 1 account new --password ./geth/password.txt --datadir ./geth > /dev/null &&
echo "[PRE-SIMULATION] Finished creating new account."

account_address=`python3.10 ./geth/scripts/build-genesis.py` &&
echo "[PRE-SIMULATION] Finished creating genesis.json."

geth --verbosity 1 init --datadir geth ./geth/genesis.json > /dev/null &&
echo "[PRE-SIMULATION] Finished initializing blockchain."

echo "[PRE-SIMULATION] Running geth client..."
geth --datadir ./geth \
     --nat extip:$ip_addr \
     --networkid 123 \
     --netrestrict $ip_addr/24 \
     --port 30303 \
     --authrpc.port 8551 \
     --http \
     --http.port $http_port \
     --http.api personal,eth,net,web3,admin,txpool \
     --allow-insecure-unlock \
     --mine \
     --miner.gasprice 0 \
     --unlock $account_address \
     --password ./geth/password.txt \
     --verbosity 1 &

s=10
echo "[PRE-SIMULATION] Sleep for $s seconds to wait for geth to stabilize..."
sleep $s
echo "[PRE-SIMULATION] Finished sleeping."

contract_address=`python3.10 ./geth/scripts/deploy-contract.py $http_port` &&
echo "[PRE-SIMULATION] Finished deploying contract into the blockchain."

echo "------------------------------SIMULATION----------------------------------"

sys_type="$1"

if [ "$sys_type" == "with-srp" ]; then
     itp="$2"
     echo "[Simulation] Running test suite for $sys_type-itp-$itp system variation..."
     python3.10 ./simulations/run-test-suite.py $sys_type $http_port $contract_address $itp > "./simulations/logs/$sys_type-$itp.txt"
elif [ "$sys_type" == "without-srp" ]; then
     echo "[Simulation] Running test suite for $sys_type system variation..."
     python3.10 ./simulations/run-test-suite.py $sys_type $http_port $contract_address > "./simulations/logs/$sys_type.txt"
elif [ "$sys_type" == "without-mndp" ]; then
     echo "[Simulation] Running test suite for $sys_type system variation..."
     python3.10 ./simulations/run-test-suite.py $sys_type > "./simulations/logs/$sys_type.txt"
else
     echo "Error: Invalid system type!"
     exit 1
fi

echo "-----------------------------POST-SIMULATION------------------------------"

pid=`ps | grep geth | sed 's@^[^0-9]*\([0-9]\+\).*@\1@'`
kill $pid &&
echo "[POST-SIMULATION] Finished killing geth process"