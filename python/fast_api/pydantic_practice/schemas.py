from datetime import date
from enum import Enum
from pydantic import BaseModel, field_validator

class GenreURLChoices(str, Enum):
    ROCK = "rock"
    METAL = "metal" 
    ELECTRONIC = "electronic"
    POP_ROCK = "pop-rock"
    GRUNGE = "grunge"

class GenreChoices(str, Enum):
    ROCK = "Rock"
    METAL = "Metal"
    ELECTRONIC = "Electronic"
    POP_ROCK = "Pop-Rock"
    GRUNGE = "Grunge"

class Album(BaseModel):
    """Schema for an album."""
    title: str
    release_date: date  # date format YYYY-MM-DD

class BandBase(BaseModel):
    """Base schema for a band (shared fields)."""
    name: str
    genre: GenreChoices
    albums: list[Album] = []

class BandCreate(BandBase):
    """Schema for creating a new band (request body)."""
    @field_validator('genre', mode="before")
    def title_case_genre(cls, value):
        """
        Normalize the genre field before validation.

        Converts the provided genre string to Title Case
        (e.g., "rock" → "Rock", "pop-rock" → "Pop-Rock")
        so it matches the `GenreChoices` Enum.
        """
        return value.title()

class BandWithID(BandBase):
    """Schema for band with ID (responses)."""
    id: int

