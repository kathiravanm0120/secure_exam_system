"""Blockchain abstraction.

Default backend remains the local demo ledger. Set BLOCKCHAIN_BACKEND=fabric
only when a Hyperledger Fabric Gateway integration is configured.
"""
from __future__ import annotations
import os
from typing import Any


def _backend():
    name = os.getenv("BLOCKCHAIN_BACKEND", "local").lower()
    if name == "fabric":
        from app.blockchain.fabric_gateway import FabricGateway
        return FabricGateway()
    from app.blockchain.ledger import LocalLedger
    return LocalLedger()


def add_event(event: str, data: dict[str, Any]) -> dict[str, Any]:
    return _backend().add_event(event, data)


def get_chain() -> list[dict[str, Any]]:
    return _backend().get_chain()


def verify_chain() -> dict[str, Any]:
    return _backend().verify_chain()


def find_question_events(question_id: int) -> list[dict[str, Any]]:
    return _backend().find_question_events(question_id)
