from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.police import PoliceLogin, Token
from app.models.police import Police
from app.db.config import SessionLocal
from app.utils import verify_password, create_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import Settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/police/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_police_by_username(db: Session, username: str):
    return db.query(Police).filter(Police.username == username).first()

def authenticate_police(db: Session, username: str, password: str):
    police = get_police_by_username(db, username)
    if not police or not verify_password(password, police.hashed_password):
        return None
    return police

async def get_current_police(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=Settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception
    police = get_police_by_username(db, username=username)
    if police is None:
        raise credentials_exception
    return police

@router.post("/police/login", response_model=Token)
def login(police_data: PoliceLogin, db: Session = Depends(get_db)):
    police = authenticate_police(db, police_data.username, police_data.password)
    if not police:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": police.username})
    return {"access_token": access_token, "token_type": "bearer"}
