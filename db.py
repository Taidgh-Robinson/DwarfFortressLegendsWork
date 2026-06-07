import json
import os

from sqlmodel import SQLModel, create_engine, Session


def _serialize_sqlmodel(obj):
    if isinstance(obj, SQLModel):
        return obj.model_dump()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://dfuser:dfpass@localhost:5432/dflegends',
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    json_serializer=lambda obj: json.dumps(obj, default=_serialize_sqlmodel),
)


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
