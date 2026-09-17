"""Application-level envelope encryption for exam questions.

Prototype model:
- AES-256-GCM encrypts each question/answer payload with a fresh data key.
- RSA-OAEP encrypts (wraps) that data key with the authority public key.
- The RSA private key is loaded from a protected PEM file for local development.

Production: replace local PEM loading with an HSM/KMS integration. Do not put
private keys in source control or in the database.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_DIR = Path(os.getenv("KEY_DIR", "./keys"))
PRIVATE_KEY_PATH = Path(os.getenv("AUTHORITY_PRIVATE_KEY", str(KEY_DIR / "authority_private.pem")))
PUBLIC_KEY_PATH = Path(os.getenv("AUTHORITY_PUBLIC_KEY", str(KEY_DIR / "authority_public.pem")))


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data.encode("ascii"))


def _ensure_authority_keypair() -> None:
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return

    PRIVATE_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    PRIVATE_KEY_PATH.write_bytes(private_bytes)
    PUBLIC_KEY_PATH.write_bytes(public_bytes)

    # Best effort for local development. Production should use OS/KMS/HSM controls.
    try:
        os.chmod(PRIVATE_KEY_PATH, 0o600)
    except OSError:
        pass


def _load_private_key():
    _ensure_authority_keypair()
    return serialization.load_pem_private_key(PRIVATE_KEY_PATH.read_bytes(), password=None)


def _load_public_key():
    _ensure_authority_keypair()
    return serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())


def encrypt_question(content: str, answer: str) -> dict[str, str]:
    """Return encrypted content/answer plus integrity hash and wrapped DEK."""
    dek = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(dek)
    nonce = os.urandom(12)

    payload = json.dumps(
        {"content": content, "answer": answer},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    ciphertext = aes.encrypt(nonce, payload, None)

    wrapped_dek = _load_public_key().encrypt(
        dek,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    content_hash = hashlib.sha256(payload).hexdigest()

    return {
        "encrypted_content": _b64(ciphertext),
        "encryption_nonce": _b64(nonce),
        "wrapped_key": _b64(wrapped_dek),
        "content_hash": content_hash,
        "crypto_version": "v1-AES256GCM-RSA3072OAEP-SHA256",
    }


def decrypt_question(encrypted_content: str, encryption_nonce: str, wrapped_key: str, content_hash: str) -> tuple[str, str]:
    """Decrypt and integrity-check an encrypted question."""
    wrapped = _unb64(wrapped_key)
    dek = _load_private_key().decrypt(
        wrapped,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aes = AESGCM(dek)
    payload = aes.decrypt(_unb64(encryption_nonce), _unb64(encrypted_content), None)

    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash != content_hash:
        raise ValueError("Question integrity check failed")

    obj = json.loads(payload.decode("utf-8"))
    return obj["content"], obj["answer"]
