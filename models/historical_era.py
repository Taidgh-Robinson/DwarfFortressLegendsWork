from sqlmodel import Field, SQLModel

class HistoricalEra(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    start_year: int
