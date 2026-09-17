#!/usr/bin/env bash
# Shell script to deploy secureexam chaincode onto Hyperledger Fabric test-network.
set -euo pipefail

echo "============================================================"
echo " Deploying Secure Exam System Chaincode to Fabric Test Net "
echo "============================================================"

# Environment configuration
FABRIC_PATH="${FABRIC_PATH:-$HOME/fabric-samples/test-network}"
CHANNEL_NAME="${CHANNEL_NAME:-mychannel}"
CHAINCODE_NAME="${CHAINCODE_NAME:-secureexam}"
CHAINCODE_PATH="${CHAINCODE_PATH:-$(pwd)/../chaincode-go/secureexam}"

if [ ! -d "$FABRIC_PATH" ]; then
  echo "Error: Fabric test-network directory not found at $FABRIC_PATH."
  echo "Please install Hyperledger Fabric binaries & samples first."
  exit 1
fi

cd "$FABRIC_PATH"

echo "[1/3] Bringing down existing network (if any)..."
./network.sh down

echo "[2/3] Starting network with CA and creating channel '$CHANNEL_NAME'..."
./network.sh up createChannel -c "$CHANNEL_NAME" -ca

echo "[3/3] Deploying Go chaincode '$CHAINCODE_NAME'..."
./network.sh deployCC -c "$CHANNEL_NAME" -ccn "$CHAINCODE_NAME" -ccp "$CHAINCODE_PATH" -ccl go

echo "============================================================"
echo " Chaincode '$CHAINCODE_NAME' successfully deployed! "
echo " Set BLOCKCHAIN_BACKEND=fabric in your backend environment. "
echo "============================================================"
