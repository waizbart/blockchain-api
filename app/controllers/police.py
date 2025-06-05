from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.police import PoliceLogin, Token
from app.models.police import Police
from app.db.config import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.services.auth_service import AuthService
from app.services.blockchain_service import BlockchainService

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


def get_blockchain_service() -> BlockchainService:
    return BlockchainService()


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


@router.get("/status")
def get_system_status(
    _: Police = Depends(get_current_police),
    blockchain_service: BlockchainService = Depends(get_blockchain_service)
):
    """
    Returns the status of the blockchain account, including balance and
    estimated number of remaining reports.
    """
    try:
        balance = blockchain_service.get_balance()
        cost_per_report = blockchain_service.estimate_report_cost()

        if cost_per_report > 0:
            remaining_reports = int(balance / cost_per_report)
        else:
            remaining_reports = float('inf')  # Avoid division by zero

        return {
            "account_balance_matic": balance,
            "estimated_cost_per_report_matic": cost_per_report,
            "estimated_remaining_reports": remaining_reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
