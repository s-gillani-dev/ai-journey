"""
main.py

Entry point of the FastAPI application.
Includes app creation, lifespan event for DB initialization,
and router registration for API endpoints.
"""
from typing import List, Optional, Annotated
from models import Band, BandCreate, Album, GenreURLChoices
from fastapi import FastAPI, Depends, HTTPException, Path, Query
from sqlmodel import Session, select
from db import get_session  # Import your init_db function


# Create the app
app = FastAPI(
    title="Bands API",
    description="A simple FastAPI application to explore bands and their genres.",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Hello from Bands API!"}

@app.post("/bands", response_model=Band)
async def create_band(
    band_data: BandCreate,
    session: Session = Depends(get_session)
) -> Band:
    """
    Create a new band and optionally its albums.

    Args:
        band_data (BandCreate): Input data containing the band's name, genre,
            and an optional list of albums.
        session (Session): Database session dependency.

    Returns:
        Band: The newly created band, including its albums if provided.
    """
    band = Band(name=band_data.name, genre=band_data.genre)
    session.add(band)
    if band_data.albums:
        for album in band_data.albums:
            album_obj = Album(title=album.title, release_date=album.release_date, band=band)
            session.add(album_obj)

    session.commit()
    session.refresh(band)
    return band


@app.get("/bands/{band_id}", response_model=Band)
async def get_band(
    band_id: int = Path(..., title="The band ID", description="Unique identifier of the band"),
    session: Session = Depends(get_session)
) -> Band:
    """
    Retrieve a band by its ID.

    Args:
        band_id (int): Unique identifier of the band to fetch.
        session (Session): Database session dependency.

    Raises:
        HTTPException: If no band with the given ID exists (404).

    Returns:
        Band: The band with the specified ID, including related albums.
    """
    band = session.get(Band, band_id)
    if not band:
        raise HTTPException(status_code=404, detail=f"Band with ID {band_id} not found")

    return band

@app.get("/bands", response_model=List[Band])
async def get_bands(
    genre: Optional[GenreURLChoices] = Query(
        default=None,
        description="Filter bands by genre (e.g., rock, metal, electronic)."
    ),
    q: Annotated[Optional[str], Query(max_length=10, description="Search band by name")] = None,
    session: Session = Depends(get_session)
) -> List[Band]:
    """
    Fetch all bands from the database, with optional filtering.

    - **genre**: filter by `GenreURLChoices`
    - **q**: case-insensitive substring match on band name
    """
    statement = select(Band)
    print("statement---------", statement)

    if genre:
        statement = statement.where(Band.genre == genre.value.title())
    if q:
        statement = statement.where(Band.name.ilike(f"%{q}%"))

    results = session.exec(statement).all()
    return results