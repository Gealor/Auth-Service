import hashlib
import bcrypt


def hash_tokens(
    token: str,
) -> bytes:
    token_sha256 = hashlib.sha256(token.encode("utf-8")).hexdigest()

    salt = bcrypt.gensalt()
    token_bytes: bytes = token_sha256.encode("utf-8")
    return bcrypt.hashpw(token_bytes, salt)


def compare_hashed_tokens(
    raw_token: bytes,
    hashed_token: bytes,
) -> bool:
    token_sha256 = hashlib.sha256(raw_token).hexdigest().encode("utf-8")
    return bcrypt.checkpw(token_sha256, hashed_token)