param (
    [Parameter(Mandatory=$true)]
    [string]$bootnode
)

geth --datadir node2 `
     --networkid 123 `
     --bootnodes $bootnode `
     --netrestrict 192.168.5.220/24 `
     --port 30304 `
     --authrpc.port 8552 `
     --ipcpath node2.ipc `
     --http `
     --http.port 8546 `
     --http.api personal,eth,net,web3,admin,txpool `
     --allow-insecure-unlock `
     --mine `
     --miner.gasprice 0 `
     --unlock 446b88179f2f7ed5ecb8a871340b0fbee76fc95f