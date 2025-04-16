
from models.label_request import LabelRequest
from models.label_response import LabelResponse

class UPSShipEngine:
    async def create_label(self, request: LabelRequest) -> LabelResponse:
        # TODO: Stub only. Implement later if needed.
        return LabelResponse(
            tracking_number="TEST-UPS-987654",
            label_url="/static/labels/TEST-UPS-987654.pdf",
            carrier="ups"
        )
