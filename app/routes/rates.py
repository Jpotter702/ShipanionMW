from fastapi import APIRouter, HTTPException
from models.rate_request import RateRequest
from models.rate_response import RateResponse
from rates.rate_service import RateService
from typing import Dict

router = APIRouter()
rate_service = RateService()

@router.post("/get-rates", response_model=RateResponse)
async def get_rates(request: RateRequest) -> RateResponse:
    """
    Get shipping rates for a package.
    
    Args:
        request: RateRequest containing shipping details
        
    Returns:
        RateResponse with cheapest and fastest options
        
    Raises:
        HTTPException: If no valid rates are found or other errors occur
    """
    try:
        return await rate_service.get_rates(request)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/carrier-status", response_model=Dict[str, bool])
async def get_carrier_status() -> Dict[str, bool]:
    """
    Get the status of carrier API connections.
    
    Returns:
        Dictionary with carrier status (True if working, False if not)
    """
    try:
        return await rate_service.validate_carriers()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking carrier status: {str(e)}"
        ) 