# Key Management & Cryptographic Hardening

## Development vs. Production Model

### Development Model
- The application automatically generates a 3072-bit RSA keypair in `./keys/` (`authority_private.pem` and `authority_public.pem`).
- `os.chmod(PRIVATE_KEY_PATH, 0o600)` restricts local file permissions.
- Public key wraps 256-bit AES-GCM data encryption keys (DEK) for questions.
- Private key un-wraps DEKs during authorized JIT question delivery.

### Production Hardening Guidelines
1. **HSM / Cloud KMS Integration**: Replace local PEM file loading with AWS KMS, Azure Key Vault, or HashiCorp Vault transit secrets engine.
2. **No Hardcoded Secrets**: Ensure `.env` is listed in `.gitignore` and `.env.example` provides template variables without real secrets.
3. **Key Rotation Protocol**:
   - Issue new RSA Key Version (e.g. `v2-RSA3072`).
   - Re-wrap existing question DEKs with the new public key without decrypting underlying question ciphertext.
4. **Key Revocation Protocol**:
   - Flag compromised key IDs in database key registry.
   - Instantly deny decryption requests referencing revoked key IDs.
