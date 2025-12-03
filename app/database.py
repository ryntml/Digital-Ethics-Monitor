import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# .env dosyasını yükle
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL .env dosyasında tanımlı değil!")

# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,      # SQL sorgularını terminalde görmek istersen güzel
    future=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


# Her request için DB session sağlayan dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
