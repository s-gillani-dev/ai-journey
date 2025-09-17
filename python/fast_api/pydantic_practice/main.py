from fastapi import FastAPI
from endpoints import bands_api_basic, bands_api_annotated

app = FastAPI(title="Pydantic Practice API")

# Register routers
app.include_router(bands_api_basic.router)
app.include_router(bands_api_annotated.router)

@app.get("/")
async def root():
    return {"message": "Hello from Pydantic Practice!"}
