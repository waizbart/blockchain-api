from app.db.config import SessionLocal
from app.models.user import User, UserRole
from app.utils.jwt import get_password_hash


def seed_users():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin_password = 'teste123'
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash(admin_password),
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            print("Usuário admin criado com sucesso! Senha: " + admin_password)
        else:
            print("Usuário admin já existe.")

        if not db.query(User).filter(User.username == "user_test").first():
            user_password = 'teste123'
            user = User(
                username="user",
                email="user@example.com",
                hashed_password=get_password_hash(user_password),
                role=UserRole.USER
            )
            db.add(user)
            db.commit()
            print("Usuário teste criado com sucesso! Senha: " + user_password)
        else:
            print("Usuário teste já existe.")

    except Exception as e:
        db.rollback()
        print("Erro ao criar usuários:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
