from sqlmodel import Field, SQLModel

class MusicalForm(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str 