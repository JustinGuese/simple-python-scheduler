from datetime import datetime
from os import environ

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = "postgresql+psycopg2://" + environ.get(
    "PSQL_URI", "postgres:postgres@localhost:5432/postgres"
)  # user:password@postgresserver/db

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
    # echo=True # debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# class bot
class Schedule(Base):
    __tablename__ = "schedules"
    bot_name = Column(String, unique=True, primary_key=True)
    cron_schedule = Column(String)
    folder = Column(String)
    file = Column(String)


class RunResult(Base):
    __tablename__ = "run_results"
    timestamp = Column(DateTime, primary_key=True, default=datetime.utcnow)
    bot_name = Column(String, primary_key=True)
    success = Column(Boolean)
    error = Column(String, nullable=True)
    logs = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)
