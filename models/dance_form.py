from sqlmodel import Field, SQLModel

class DanceForm(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str 