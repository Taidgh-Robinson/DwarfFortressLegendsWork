from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON

class Structure(SQLModel, table=False):
    local_id: int
    type: str
    name: Optional[str] = None
    copied_artifact_ids: list[int] = []

class Site(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    type: str
    name: str
    coords: str
    rectangle: str
    structures: list[Structure] = Field(default_factory=list, sa_column=Column(JSON))
