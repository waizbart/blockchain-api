from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.controllers.police import Police


class PoliceRepository(BaseRepository[Police]):
    def __init__(self, db: Session):
        super().__init__(db, Police)

    def get_by_username(self, username: str) -> Optional[Police]:
        """
        Get police user by username.
        """
        return self.db.query(self.model).filter(self.model.username == username).first()

    def authenticate(self, username: str, password: str) -> Optional[Police]:
        """
        Authenticate a police user with username and password.
        """
        user = self.get_by_username(username)
        if not user:
            return None
        from app.core.security import verify_password
        if not verify_password(password, user.hashed_password):
            return None
        return user
