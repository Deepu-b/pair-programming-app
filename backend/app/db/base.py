from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# For a prototype, you can use SQLite to start, but requirements asked for Postgres.
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# For now, let's use SQLite so you can run it immediately without Docker setup, 
# but structuring it so it's easily swappable for Postgres.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()