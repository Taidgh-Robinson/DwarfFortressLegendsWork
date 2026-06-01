from typing import Optional
from sqlmodel import Field, SQLModel

class UndergroundRegion(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    type: str 
    depth: int