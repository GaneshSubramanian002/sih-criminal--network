from pydantic import BaseModel, Field

class TextIn(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=1)

class EntityOut(BaseModel):
    id: int
    name: str
    entity_type: str
    source: str | None = None
    confidence: float

    class Config:
        from_attributes = True
