from passlib.context import CryptContext

import os
from sqlalchemy.orm import Session
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def seed_admin_user(db: Session):
    existing = db.query(User).first()
    if existing:
        return  # already seeded, do nothing

    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        print("⚠️  ADMIN_USERNAME/ADMIN_PASSWORD not set — skipping admin seed.")
        return

    admin = User(username=username, hashed_password=hash_password(password))
    db.add(admin)
    db.commit()
    print(f"✅ Admin user '{username}' created.")