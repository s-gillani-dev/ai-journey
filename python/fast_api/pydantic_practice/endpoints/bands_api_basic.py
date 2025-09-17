from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
from schemas import BandCreate, BandWithID, GenreURLChoices
from bands_data import BANDS

# Create router instead of app
router = APIRouter(prefix="/basic", tags=["Bands (Basic)"])

BANDS_BY_ID = {b["id"]: BandWithID(**b) for b in BANDS}


@router.get("/", response_model=dict)
async def index() -> dict[str, str]:
    return {"hello": "world"}


@router.get("/bands", response_model=List[BandWithID])
async def get_bands(genre: Optional[GenreURLChoices] = None, q: Optional[str] = None) -> List[BandWithID]:
    q_lower = q.lower() if q else None
    return [
        BandWithID(**b)
        for b in BANDS
        if (not genre or b["genre"].lower() == genre.value)
        and (not q_lower or q_lower in b["name"].lower())
    ]


@router.get("/bands/{band_id}", response_model=BandWithID)
async def get_band(band_id: int = Path(..., title="The band ID")) -> BandWithID:
    band = BANDS_BY_ID.get(band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    return band


@router.get("/bands/genre/{genre}", response_model=List[BandWithID])
async def get_bands_by_genre(genre: GenreURLChoices) -> List[BandWithID]:
    return [BandWithID(**b) for b in BANDS if b["genre"].lower() == genre.value]


@router.post("/bands", response_model=BandWithID)
async def create_band(band: BandCreate) -> BandWithID:
    next_id = BANDS[-1]['id'] + 1
    new_band = BandWithID(id=next_id, **band.model_dump()).model_dump()
    BANDS.append(new_band)
    BANDS_BY_ID[new_band['id']] = new_band
    return new_band
