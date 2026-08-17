from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from darknight.services.config.settings import get_app_config

_database = get_app_config().database

IS_SQLITE = _database.url.startswith('sqlite')

if IS_SQLITE:
    engine = create_engine(
        _database.url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        _database.url,
        pool_size=_database.pool_size,
        max_overflow=_database.max_overflow,
        pool_recycle=3600,
        pool_timeout=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
