#!/bin/bash

# Command 1
# ./run.sh "192.168.1.5" "8545" "with-srp" "ocsvm" "-0.30" "hans"

# Command 2
./run_copy.sh "192.168.1.5" "8545" "with-srp" "ocsvm" "-0.15" "hans"
./copy.sh

# Command 3
./run.sh "192.168.1.5" "8545" "with-srp" "ocsvm" "0.0" "hans"
./copy.sh

# Command 4
./run.sh "192.168.1.5" "8545" "with-srp" "lof" "-0.30" "hans"
./copy.sh

# Command 5
./run.sh "192.168.1.5" "8545" "with-srp" "lof" "-0.15" "hans"
./copy.sh

# Command 6
./run.sh "192.168.1.5" "8545" "with-srp" "lof" "0.0" "hans"
./copy.sh

# Command 7
sleep 2
./copy.sh
