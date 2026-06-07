from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON

class HistoricalEventCollection(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    start_year: int
    start_seconds72: Optional[int] = None
    end_year: int
    end_seconds72: Optional[int] = None
    type: str
    civ_id: Optional[int] = None
    occasion_id: Optional[int] = None
    ordinal: Optional[int] = None
    event_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    eventcol_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))
