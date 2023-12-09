import datetime as dt
from typing import NamedTuple
from jose import jwt

jwt_secret_key = "fjdlasjroj3oi4o12j4oi3j1oi4nguoda"
jwt_algorithm = "HS256"
jwt_hash_algorithm = "HS256"


class UserTokenData(NamedTuple):
    """Данные которые хранятся в jwt токене пользователя
    user_id: int
    email: str
    role_id: int
    exp: dt.datetime
    """

    user_id: int
    email: str
    role_id: int
    exp: dt.datetime


# UserTokenData = namedtuple("UserTokenData", ["user_id", "email", "role_id", "exp"])


class JWTEncoder:
    @staticmethod
    def create_jwt_token(
        data: dict[str, str | dt.datetime | int],
        expires_delta: dt.timedelta = dt.timedelta(days=1),
    ):
        to_encode = data.copy()
        to_encode["exp"] = dt.datetime.utcnow() + expires_delta
        return jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)

    @staticmethod
    def decode_jwt(token: str) -> dict[str, str | dt.datetime]:
        return jwt.decode(token, jwt_secret_key, jwt_hash_algorithm)

    @staticmethod
    def create_access_token(
        user_id: int,
        email: str,
        role_id: int,
        expires_delta: dt.timedelta = dt.timedelta(days=1),
    ) -> str:
        to_encode = {
            "user_id": user_id,
            "email": email,
            "role_id": role_id,
            "exp": dt.datetime.utcnow() + expires_delta,
        }
        return jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_hash_algorithm)

    @staticmethod
    def decode_access_token(token: str) -> UserTokenData:
        return UserTokenData(**jwt.decode(token, jwt_secret_key, jwt_hash_algorithm))
