from app.db.config import SessionLocal
from app.models.police import Police
from app.utils import get_password_hash
import secrets
import string

def seed_police_user():
    db = SessionLocal()
    try:
        if not db.query(Police).filter(Police.username == "admin").first():
            password = 'teste123'
            admin = Police(
                username="admin",
                hashed_password=get_password_hash(password)
            )
            db.add(admin)
            db.commit()
            print("Usuário admin criado com sucesso! Senha: " + password)
        else:
            print("Usuário admin já existe.")
    except Exception as e:
        db.rollback()
        print("Erro ao criar seed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_police_user()
