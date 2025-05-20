from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.repositories.police import PoliceRepository
from app.controllers.police import Police
from app.services.token_service import TokenService  # Import TokenService


class AuthService:
    """
    Service for handling authentication and authorization.
    """

    def __init__(
        self,
        db: Session,
        secret_key: str,
        algorithm: str = "HS256",
        token_expire_minutes: int = 30
    ):
        self.repository = PoliceRepository(db)
        self.token_service = TokenService(secret_key, algorithm, token_expire_minutes)

    def authenticate_user(self, username: str, password: str) -> Optional[Police]:
        """
        Authenticate a user with username and password.
        """
        return self.repository.authenticate(username, password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token using TokenService.
        """
        return self.token_service.create_access_token(data)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and verify a JWT token using TokenService.
        """
        return self.token_service.decode_token(token)

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
