# We will use this for the reader node
param (
    [Parameter(Mandatory=$true)]
    [string]$bootnode
)

geth --datadir node4 `
     --networkid 123 `
     --bootnodes $bootnode `
     --netrestrict 192.168.5.220/24 `
     --port 30306 `
     --authrpc.port 8554 `
     --ipcpath node4.ipc `
     --http `
     --http.port 8548 `
     --http.api personal,eth,net,web3,admin,txpool `
     --allow-insecure-unlock `
     --unlock 274d55399c713f71c952f7c49700c3bf8aca5b48