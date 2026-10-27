"""Single SQLAlchemy declarative registry for every application model."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
