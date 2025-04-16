
from fastapi import APIRouter, HTTPException
from models.label_request import LabelRequest
from models.label_response import LabelResponse
from labels.label_creator import LabelCreator

router = APIRouter()

@router.post("/labels", response_model=LabelResponse)
async def create_label(request: LabelRequest):
    try:
        creator = LabelCreator()
        return await creator.create_label(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Label creation failed: {str(e)}")
