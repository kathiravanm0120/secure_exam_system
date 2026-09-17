"""Optional Hyperledger Fabric Gateway client.

This adapter is intentionally disabled unless BLOCKCHAIN_BACKEND=fabric and
all Fabric Gateway settings are supplied. The normal local prototype remains
fully functional without Fabric infrastructure.
"""
from __future__ import annotations
import os

class FabricGateway:
    def __init__(self):
        try:
            from fabric_gateway import Gateway, GatewayError  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Fabric backend requested, but the Fabric Gateway client is not installed. "
                "Run the Fabric test network/client setup and install the selected SDK."
            ) from exc
        self.Gateway = Gateway
        self.GatewayError = GatewayError
        self.channel = os.environ["FABRIC_CHANNEL"]
        self.chaincode = os.environ["FABRIC_CHAINCODE"]
        self.msp_id = os.environ["FABRIC_MSP_ID"]
        self.cert_path = os.environ["FABRIC_CERT_PATH"]
        self.key_path = os.environ["FABRIC_KEY_PATH"]
        self.tls_cert_path = os.environ["FABRIC_TLS_CERT_PATH"]
        self.peer_endpoint = os.environ["FABRIC_PEER_ENDPOINT"]
        self._network = None

    def _network_handle(self):
        # Gateway API differs slightly by SDK release; keep the connection
        # construction in one place so the rest of the app is SDK-independent.
        if self._network is None:
            self._network = self.Gateway.from_msp_identity(
                msp_id=self.msp_id,
                certificate=self.cert_path,
                private_key=self.key_path,
                tls_cert=self.tls_cert_path,
                peer_endpoint=self.peer_endpoint,
                channel=self.channel,
                chaincode=self.chaincode,
            )
        return self._network

    def add_event(self,event,data):
        # Chaincode transaction; event data is sent as canonical JSON.
        return self._network_handle().submit_transaction("RecordEvent", event, _json(data))
    def get_chain(self):
        raw=self._network_handle().evaluate_transaction("GetEvents")
        return _loads(raw)
    def verify_chain(self):
        raw=self._network_handle().evaluate_transaction("VerifyChain")
        return _loads(raw)
    def find_question_events(self,question_id):
        raw=self._network_handle().evaluate_transaction("GetQuestionEvents", str(question_id))
        return _loads(raw)

def _json(obj):
    import json; return json.dumps(obj, sort_keys=True, separators=(",", ":"))
def _loads(raw):
    import json
    if isinstance(raw,(bytes,bytearray)): raw=raw.decode()
    return json.loads(raw)
