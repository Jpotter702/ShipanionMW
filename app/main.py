from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import rates

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

@app.get("/")
async def root():
    return {"message": "Welcome to ShipVox API"}
