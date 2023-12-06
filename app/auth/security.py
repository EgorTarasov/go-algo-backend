import uuid

from passlib.context import CryptContext


class PasswordManager:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)


def encode_uuid3(data: str) -> uuid.UUID:
    return uuid.uuid3(uuid.UUID("35243bc9-5acd-4d05-a02b-1494dd5dee33"), data)
