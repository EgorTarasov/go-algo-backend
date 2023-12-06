from .jwt import JWTEncoder
from .security import PasswordManager
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

__all__ = ["JWTEncoder", "PasswordManager", "oauth2_scheme"]
