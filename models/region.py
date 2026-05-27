from typing import Optional
from sqlmodel import Field, SQLModel

class Region(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str 
    type: str