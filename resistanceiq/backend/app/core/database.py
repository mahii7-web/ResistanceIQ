from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

def normalize_database_url(url: str) -> str:
    """
    Safely normalizes database connection URLs for PostgreSQL and SQLite.
    Normalizes legacy 'postgres://' or driverless 'postgresql://' to modern 'postgresql+psycopg://'
    for SQLAlchemy 2.0 with Psycopg 3. Preserves explicit driver schemes (e.g. postgresql+psycopg2://).
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


db_url = normalize_database_url(settings.DATABASE_URL)

connect_args = {}
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    if "sslmode=" not in db_url.lower():
        connect_args["sslmode"] = "require"
    connect_args["connect_timeout"] = 10
    engine_kwargs["connect_args"] = connect_args
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    })

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
