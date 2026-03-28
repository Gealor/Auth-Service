import copy
import datetime
from pathlib import Path
import jwt
from core.config import settings
from schemas.user_schemas import UserInfoForAdmin

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type,
    }
    jwt_payload.update(token_data)

    token = encode_jwt(payload=jwt_payload, expire_minutes=expire_minutes)
    return token


def create_access_token(user: UserInfoForAdmin) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "role": user.role.name,
    }

    access_token = create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth.access_token_expire_minutes,
    )
    return access_token


def create_refresh_token(user: UserInfoForAdmin) -> str:
    # в рефреш токене не хранится динамическая информация, т.е. которая может измениться в будущем.
    jwt_payload = {
        "sub": str(user.id),
    }

    refresh_token = create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth.refresh_token_expire_minutes,
    )
    return refresh_token


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key.read_text(),  # получаю содержимое файла с помощью read_text библиотеки pathlib
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    exp_token = now + datetime.timedelta(minutes=expire_minutes)

    copy_payload = copy.copy(payload)
    # exp - время жизни токена, т.е. указыватся дата, после которой токен сгорает
    copy_payload.update(
        # время для iat и exp надо указывать время по utc, т.е. всемирное координированное время, универсальный мировой стандарт времени.
        # короче без учета часовых поясов
        exp=exp_token,
        iat=now,
    )
    encoded = jwt.encode(copy_payload, private_key, algorithm=algorithm)
    return encoded

def decode_jwt(
    jwt_token: str | bytes,
    public_key: str = settings.auth.public_key.read_text(),
    algorithm: str = settings.auth.algorithm,
):
    decoded = jwt.decode(
        jwt_token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded
