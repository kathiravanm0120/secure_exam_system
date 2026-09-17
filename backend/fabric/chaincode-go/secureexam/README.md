# Secure Exam Fabric Chaincode

This chaincode records exam-security lifecycle events such as question creation,
review, approval, selection, exposure, answer submission and completion.

The actual question contents remain off-chain and encrypted. Fabric stores the
metadata/audit events needed to establish a trusted history.

## Build

From this directory:

```bash
go mod tidy
go build ./...
```

Deploy through the official Hyperledger Fabric test network or your organization's
permissioned Fabric network.
