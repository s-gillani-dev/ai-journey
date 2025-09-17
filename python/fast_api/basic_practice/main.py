from enum import Enum
from fastapi import FastAPI, HTTPException 

app = FastAPI(
    title="Bands API",
    description="A simple FastAPI application to explore bands and their genres.",
    version="1.0.0",
)

class GenreURLChoices(Enum):
    """Enum representing available music genres for bands."""
    ROCK = "rock"
    METAL = "metal"
    ELECTRONIC = "electronic"
    POP_ROCK = "pop-rock"
    GRUNGE = "grunge"


# Mock dataset of bands
BANDS = [
    {"id": 1, "name": "Pink Floyd", "genre": "Rock"},
    {"id": 2, "name": "Metallica", "genre": "Metal"},
    {"id": 3, "name": "Coldplay", "genre": "Electronic"},
    {"id": 4, "name": "Imagine Dragons", "genre": "Pop-Rock"},
    {"id": 5, "name": "Nirvana", "genre": "Grunge"},
]


@app.get("/")
async def index() -> dict[str, str]:
    """Root endpoint returning a simple hello world message."""
    return {"hello": "world"}


@app.get("/about")
async def about() -> str:
    """Provide basic information about the company."""
    return "An Exceptional Company"


@app.get("/bands")
async def bands() -> list[dict]:
    """Return a list of all available bands."""
    return BANDS


@app.get("/bands/{band_id}")
async def band(band_id: int) -> dict:
    """
    Retrieve a single band by its ID.

    Args:
        band_id (int): The unique identifier of the band.

    Raises:
        HTTPException: If the band with the given ID is not found.

    Returns:
        dict: A dictionary representing the band.
    """
    selected_band = next((b for b in BANDS if b["id"] == band_id), None)
    if selected_band is None:
        raise HTTPException(status_code=404, detail="Band not found")
    return selected_band


@app.get("/bands/genre/{genre}")
async def band_for_genre(genre: GenreURLChoices) -> list[dict]:
    """
    Retrieve bands filtered by their genre.

    Args:
        genre (GenreURLChoices): The genre to filter bands.

    Returns:
        list[dict]: A list of bands matching the given genre.
    """
    return [b for b in BANDS if b["genre"].lower() == genre.value.lower()]
