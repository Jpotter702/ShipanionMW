from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import rates, labels

app = FastAPI(
    title="ShipVox API",
    description="Shipping rate aggregation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rates.router, prefix="/api", tags=["rates"])
app.include_router(labels.router, prefix="/api", tags=["labels"])

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to ShipVox API"}
