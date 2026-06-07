from sqlmodel import Field, SQLModel

class EntityPopulation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
