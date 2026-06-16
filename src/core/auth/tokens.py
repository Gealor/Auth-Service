import hashlib

from .bcrypt_hashing import hash_with_salt, compare_bytes_with_hash


async def hash_tokens(
    token: str,
) -> bytes:
    token_sha256 = hashlib.sha256(token.encode("utf-8")).hexdigest()

    token_bytes: bytes = token_sha256.encode("utf-8")
    return await hash_with_salt(token_bytes)


async def compare_hashed_tokens(
    raw_token: bytes,
    hashed_token: bytes,
) -> bool:
    token_sha256 = hashlib.sha256(raw_token).hexdigest().encode("utf-8")
    return await compare_bytes_with_hash(token_sha256, hashed_token)
