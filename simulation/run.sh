# Usage: ./run.sh <ip_addr> <http_port> <sys_type> [<itp>]
# 
# Note: only include itp when sys_type == 'with-srp'

current_dir=${PWD##*/}

if [ "$current_dir" != "simulation" ]; then
     echo "Error: Current directory must be simulation before running this script!"
     exit 1
fi

ip_addr="$1"
http_port="$2"


x=1
for i in {001..100}
do
     rm -rf ./geth/keystore ./geth/geth ./geth/genesis.json &&
     echo "[$x] Finished removing geth artifacts from previous run."

     geth --verbosity 1 account new --password ./geth/password.txt --datadir ./geth > /dev/null &&
     echo "[$x] Finished creating new account."

     account_address=`python3.10 ./geth/scripts/build-genesis.py` &&
     echo "[$x] Finished creating genesis.json."

     geth --verbosity 1 init --datadir geth ./geth/genesis.json > /dev/null &&
     echo "[$x] Finished initializing blockchain."

     echo "[$x] Running geth client..."
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
     echo "[$x] Sleep for $s seconds to wait for geth to stabilize..."
     sleep $s
     echo "[$x] Finished sleeping."

     contract_address=`python3.10 ./geth/scripts/deploy-contract.py $http_port` &&
     echo "[$x] Finished deploying contract into the blockchain."

     sys_type="$3"

     if [ "$sys_type" == "with-srp" ]; then
          itp="$4"
          echo "[$x] Running test suite for '$sys_type-itp-$itp' system variation..."
          python3.10 ./simulations/run-test-suite.py $sys_type $http_port $contract_address $itp $x > "./simulations/logs/with-srp-$itp/test-case-$i-logs.txt"
     elif [ "$sys_type" == "without-srp" ]; then
          echo "[$x] Running test suite for '$sys_type' system variation..."
          python3.10 ./simulations/run-test-suite.py $sys_type $http_port $contract_address $x > "./simulations/logs/without-srp/test-case-$i-logs.txt"

     elif [ "$sys_type" == "without-mndp" ]; then
          echo "[$x] Running test suite for '$sys_type' system variation..."
          python3.10 ./simulations/run-test-suite.py $sys_type $x > "./simulations/logs/without-mndp/test-case-$i-logs.txt"
     else
          echo "Error: Invalid system type!"
          exit 1
     fi

     pid=`ps | grep geth | sed 's@^[^0-9]*\([0-9]\+\).*@\1@'`
     kill $pid &&
     echo "[$x] Finished killing geth process"

     echo "[$x] Sleep for $s seconds before running next test case..."
     sleep $s
     echo "[$x] Finished sleeping"

     echo "[$x] Test done!"
     python3.10 ./simulations/utils/ring.py

     x=$((x + 1))
done

