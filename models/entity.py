from typing import Optional
from sqlmodel import Field, SQLModel, Column, JSON

class Honor(SQLModel, table=False):
    id: int
    name: str
    gives_precedence: Optional[int] = None
    requires_any_melee_or_ranged_skill: Optional[bool] = None
    required_skill_ip_total: Optional[int] = None
    required_kills: Optional[int] = None
    exempt_epid: Optional[int] = None
    exempt_former_epid: Optional[int] = None
    required_skill: Optional[str] = None

class Entity(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: Optional[str] = None
    honors: list[Honor] = Field(default_factory=list, sa_column=Column(JSON))
    entity_population_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))
