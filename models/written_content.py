from typing import Optional
from sqlmodel import Field, SQLModel

class WrittenContent(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: Optional[str] = None
    author_hfid: Optional[int] = None
    author_roll: Optional[int] = None
    form: Optional[str] = None
    form_id: Optional[int] = None
