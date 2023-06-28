from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pwnedfast.config import settings

# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-sqlalchemy-engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, connect_args=settings.SQLALCHEMY_DATABASE_CONNECT_ARGS
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
