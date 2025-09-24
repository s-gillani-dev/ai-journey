"""
models.py

SQLModel models for the FastAPI application.

Includes:
- Enum classes for genres (URL-safe and display versions).
- Database models for Band and Album.
- Pydantic-style schemas for creating and validating Band/Album data.
"""

from datetime import date
from enum import Enum
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship

class GenreURLChoices(str, Enum):
    """
    Enum for URL-safe genre values.
    Used for path/query parameters in API endpoints.
    """
    ROCK = "rock"
    METAL = "metal" 
    ELECTRONIC = "electronic"
    POP_ROCK = "pop-rock"
    GRUNGE = "grunge"

class GenreChoices(str, Enum):
    """
    Enum for user-friendly genre values.
    Stored in the database and shown in responses.
    """
    ROCK = "Rock"
    METAL = "Metal"
    ELECTRONIC = "Electronic"
    POP_ROCK = "Pop-Rock"
    GRUNGE = "Grunge"

class AlbumBase(SQLModel):
    """
    Base schema for an album.

    Attributes:
        title (str): Album title.
        release_date (date): Release date of the album.
        band_id (int): Foreign key reference to the band that created the album.
    """
    title: str
    release_date: date
    band_id: int = Field(default=None, foreign_key="band.id")

class Album(AlbumBase, table=True):
    """
    Database model for an album.

    Inherits fields from AlbumBase and adds:
        id (int): Primary key.
        band (Band): Relationship to the band owning this album.
    """
    id: int = Field(default=None, primary_key=True)
    band: "Band" = Relationship(back_populates="albums")

class BandBase(SQLModel):
    """
    Base schema for a band.

    Attributes:
        name (str): Band name.
        genre (GenreChoices): Genre of the band.
    """
    name: str
    genre: GenreChoices


class BandCreate(BandBase):
    """
    Schema for creating a new band.

    Attributes:
        albums (list[AlbumBase] | None): Optional list of albums to create with the band.
    """

    albums: list[AlbumBase] | None = None

    @field_validator("genre", mode="before")
    def title_case_genre(cls, value: str) -> str:
        """
        Normalize the genre string before validation.

        Converts input to Title Case so it matches `GenreChoices`.
        Example:
            "rock" → "Rock"
            "pop-rock" → "Pop-Rock"
        """
        return value.title()

class Band(BandBase, table=True):
    """
    Database model for a band.

    Inherits from BandBase and adds:
        id (int): Primary key.
        albums (list[Album]): List of related albums (via relationship).
    """
    id: int = Field(default=None, primary_key=True)
    albums: list[Album] = Relationship(back_populates="band")
    date_formed: date | None
