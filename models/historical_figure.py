from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON

class HfLink(SQLModel, table=False):
    link_type: str
    hfid: int

class EntityLink(SQLModel, table=False):
    link_type: str
    entity_id: int

class HistoricalFigure(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    race: Optional[str] = None
    caste: Optional[str] = None
    appeared: Optional[int] = None
    birth_year: Optional[int] = None
    birth_seconds72: Optional[int] = None
    death_year: Optional[int] = None
    death_seconds72: Optional[int] = None
    associated_type: Optional[str] = None
    hf_links: list[HfLink] = Field(default_factory=list, sa_column=Column(JSON))
    entity_links: list[EntityLink] = Field(default_factory=list, sa_column=Column(JSON))
