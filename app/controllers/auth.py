from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import UserLogin, UserRegister, Token, UserResponse
from app.services.auth_service import AuthService
from app.services.blockchain_service import BlockchainService
from app.core.deps import get_db, get_auth_service, get_current_admin, get_current_active_user
from app.models.user import User

router = APIRouter()


def get_blockchain_service() -> BlockchainService:
    return BlockchainService()


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account.
    """
    try:
        user = auth_service.register_user(user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with username and password.
    """
    user = auth_service.authenticate_user(
        user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = auth_service.create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    """
    return UserResponse.from_orm(current_user)


@router.get("/admin/status")
def get_system_status(
    _: User = Depends(get_current_admin),
    blockchain_service: BlockchainService = Depends(get_blockchain_service)
):
    """
    Returns the status of the blockchain account, including balance and
    estimated number of remaining reports.
    Only accessible by admin users.
    """
    try:
        balance = blockchain_service.get_balance()
        cost_per_report = blockchain_service.estimate_report_cost()

        if cost_per_report > 0:
            remaining_reports = int(balance / cost_per_report)
        else:
            remaining_reports = float('inf')

        return {
            "account_balance_matic": balance,
            "estimated_cost_per_report_matic": cost_per_report,
            "estimated_remaining_reports": remaining_reports
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
