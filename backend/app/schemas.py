from pydantic import BaseModel
from typing import Optional

class WordBase(BaseModel):
    word: str
    meaning: str
    part_of_speech: Optional[str] = None
    example: Optional[str] = None

class WordCreate(WordBase):
    pass

class WordUpdate(BaseModel):
    meaning: Optional[str] = None
    part_of_speech: Optional[str] = None
    example: Optional[str] = None

class WordResponse(WordBase):
    id: int

