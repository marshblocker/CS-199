## Requirements
- Python 3.10 (since web3.py (a library used by the Python scripts here) is not compatible with Python 3.11)
- Run `pip install -r requirements.txt` to install the required Python packages

## Tests Checklist
- [ ] with-srp, OCSVM, threshold -1.0 (`./run.sh <ip_addr> <http_port> "with-srp" "ocsvm" "-0.30" <username>`)
- [ ] with-srp, OCSVM, threshold -0.5 (`./run.sh <ip_addr> <http_port> "with-srp" "ocsvm" "-0.15" <username>`)
- [ ] with-srp, OCSVM, threshold 0.0 (`./run.sh <ip_addr> <http_port> "with-srp" "ocsvm" "0.0" <username>`)
- [ ] with-srp, SGD-OCSVM, threshold -1.0 (`./run.sh <ip_addr> <http_port> "with-srp" "sgd-ocsvm" "-0.30" <username>`)
- [ ] with-srp, SGD-OCSVM, threshold -0.5 (`./run.sh <ip_addr> <http_port> "with-srp" "sgd-ocsvm" "-0.15" <username>`)
- [ ] with-srp, SGD-OCSVM, threshold 0.0 (`./run.sh <ip_addr> <http_port> "with-srp" "sgd-ocsvm" "0.0" <username>`)
- [ ] with-srp, LOF, threshold -1.0 (`./run.sh <ip_addr> <http_port> "with-srp" "lof" "-0.30" <username>`)
- [ ] with-srp, LOF, threshold -0.5 (`./run.sh <ip_addr> <http_port> "with-srp" "lof" "-0.15" <username>`)
- [ ] with-srp, LOF, threshold 0.0 (`./run.sh <ip_addr> <http_port> "with-srp" "lof" "0.0" <username>`)
- [ ] without-srp (`./run.sh <ip_addr> <http_port> "without-srp" <username>`)
- [ ] without-mndp (`./run.sh <ip_addr> <http_port> "without-mndp" <username>`)

`<username>` is any string identifier e.g. `kenneth`. Make sure the directories where the logs and computed metrics will be stored are created before running `run.sh` (see the directories in `./simulation/simulations/logs/kenneth` to see how the directories are named). After running the tests, check the logs in `./simulation/simulations/logs/<username>` directory and the computed metrics in `./simulation/simulations/computed-metrics/<username>` directory.