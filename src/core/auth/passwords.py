from .bcrypt_hashing import hash_with_salt, compare_bytes_with_hash


async def hash_password(
    password: str,
) -> bytes:
    pwd_bytes: bytes = password.encode("utf-8")
    return await hash_with_salt(pwd_bytes)


async def compare_hashed_passwords(
    entered_password: bytes,
    hashed_password: bytes,
) -> bool:
    return await compare_bytes_with_hash(entered_password, hashed_password)
