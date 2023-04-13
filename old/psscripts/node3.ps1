param (
    [Parameter(Mandatory=$true)]
    [string]$bootnode
)

geth --datadir node3 `
     --networkid 123 `
     --bootnodes $bootnode `
     --netrestrict 192.168.5.220/24 `
     --port 30305 `
     --authrpc.port 8553 `
     --ipcpath node3.ipc `
     --http `
     --http.port 8547 `
     --http.api personal,eth,net,web3,admin,txpool `
     --allow-insecure-unlock `
     --mine `
     --miner.gasprice 0 `
     --unlock 9e91780c3c029b7262e87d7b83fb98db7e8dfbac