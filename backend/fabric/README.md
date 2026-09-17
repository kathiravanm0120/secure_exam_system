# Hyperledger Fabric integration

Phase 9 separates the blockchain interface from the application. The FastAPI app
now talks to `app.blockchain.service` instead of directly depending on the local
JSON ledger.

- `BLOCKCHAIN_BACKEND=local` keeps the offline demo ledger.
- `BLOCKCHAIN_BACKEND=fabric` selects the Fabric adapter.
- `chaincode-go/secureexam/` contains the permissioned-ledger smart contract.

A real Fabric network requires peer/orderer/CA infrastructure and certificates.
Because this development environment does not have Docker/Fabric nodes running,
the packaged application is tested with the local backend while the Fabric chaincode
and adapter are included for deployment on a real Fabric network.
