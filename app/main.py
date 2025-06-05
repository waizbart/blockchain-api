from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.denuncia import router as denuncia_router
from app.controllers.police import router as police_router
from app.db.config import Base, engine
from app.db.seed import seed_police_user
from app.utils.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Denúncias Anônimas - Backend Blockchain",
    version="1.0.0",
    description="API para registro e listagem de denúncias anonimas na Blockchain (Polygon)."
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(denuncia_router, prefix="/api", tags=["Denúncias"])
app.include_router(police_router, prefix="/api", tags=["Acesso policial"])

seed_police_user()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
