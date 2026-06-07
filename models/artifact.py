from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON

class ArtifactItem(SQLModel, table=False):
    name_string: str
    page_number: Optional[int] = None
    page_written_content_id: Optional[int] = None

class Artifact(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str] = None
    item: Optional[ArtifactItem] = Field(default=None, sa_column=Column(JSON))
    holder_hfid: Optional[int] = None
    site_id: Optional[int] = None
