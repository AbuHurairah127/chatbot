import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

# Use the psycopg2 driver explicitly
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Supabase requires SSL for direct Postgres connections
if "sslmode=" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    age = Column(Integer, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create the users table if needed, and seed dummy rows only when empty."""
    Base.metadata.create_all(bind=engine)

    seed_users = [
        {"name": "Ali Khan", "email": "ali.khan@example.com", "age": 28},
        {"name": "Sara Ahmed", "email": "sara.ahmed@example.com", "age": 24},
        {"name": "Hassan Raza", "email": "hassan.raza@example.com", "age": 31},
        {"name": "Fatima Noor", "email": "fatima.noor@example.com", "age": 26},
        {"name": "Omar Siddiqui", "email": "omar.siddiqui@example.com", "age": 29},
    ]

    db = SessionLocal()
    try:
        if db.query(UserModel).count() == 0:
            for user in seed_users:
                db.add(UserModel(**user))
            db.commit()
    finally:
        db.close()
