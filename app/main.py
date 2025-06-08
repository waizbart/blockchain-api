from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.denuncia import router as denuncia_router
from app.controllers.auth import router as auth_router
from app.controllers.analysis import router as analysis_router
from app.db.config import Base, engine
from app.db.seed import seed_users
from app.utils.rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Denúncias Anônimas - Backend Blockchain",
    version="2.0.0",
    description="API para registro e listagem de denúncias anonimas na Blockchain (Polygon) com sistema de autenticação baseado em roles."
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

app.include_router(auth_router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(denuncia_router, prefix="/api", tags=["Denúncias"])
app.include_router(analysis_router, prefix="/api/admin",
                   tags=["Análise e Administração"])

seed_users()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
