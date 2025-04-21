from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt
from sqlalchemy.orm import Session

from app.repositories.police import PoliceRepository
from app.controllers.police import Police


class AuthService:
    """
    Service for handling authentication and authorization.
    """

    def __init__(self, db: Session, secret_key: str, algorithm: str = "HS256", token_expire_minutes: int = 30):
        self.repository = PoliceRepository(db)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes

    def authenticate_user(self, username: str, password: str) -> Optional[Police]:
        """
        Authenticate a user with username and password.
        """
        return self.repository.authenticate(username, password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify a JWT token.
        """
        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            return payload
        except jwt.JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[Police]:
        """
        Get the current user from a token.
        """
        payload = self.decode_token(token)
        if payload is None:
            return None

        username = payload.get("sub")
        if username is None:
            return None

        return self.repository.get_by_username(username)
