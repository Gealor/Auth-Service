import asyncio
import bcrypt

async def hash_with_salt(string: bytes) -> bytes:
    salt = bcrypt.gensalt()

    return await asyncio.to_thread(bcrypt.hashpw, string, salt)
# в bcrypt тяжелые и долгие операции, но они также являются C-расширениям, а значит отпускают GIL, а следовательно не блокируют многопоточность

async def compare_bytes_with_hash(entered: bytes, hashed: bytes) -> bool:
    return await asyncio.to_thread(bcrypt.checkpw, entered, hashed)