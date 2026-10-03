from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.environ["DATABASE_URL"]
elif os.getenv("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/finsight.db"
else:
    DATABASE_URL = "sqlite:///data/processed/finsight.db"

if DATABASE_URL.startswith("sqlite:///data/"):
    os.makedirs("data/processed", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
