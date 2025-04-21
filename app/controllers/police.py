from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.police import PoliceLogin, Token
from app.models.police import Police
from app.db.config import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.services.auth_service import AuthService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/police/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db, settings.SECRET_KEY)


async def get_current_police(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    police = auth_service.get_current_user(token)
    if police is None:
        raise credentials_exception

    return police


@router.post("/police/login", response_model=Token)
def login(
    police_data: PoliceLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    police = auth_service.authenticate_user(
        police_data.username, police_data.password)
    if not police:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token = auth_service.create_access_token(
        data={"sub": police.username})
    return {"access_token": access_token, "token_type": "bearer"}
