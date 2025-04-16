
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LabelResponse(BaseModel):
    tracking_number: str
    label_url: str
    native_qr_code_base64: Optional[str] = None
    fallback_qr_code_url: Optional[str] = None
    carrier: str
    estimated_delivery: Optional[datetime]
