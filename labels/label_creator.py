
from labels.fedex_ship import FedExShipEngine
from labels.ups_ship import UPSShipEngine
from labels.qr_generator import generate_qr_code
from models.label_request import LabelRequest
from models.label_response import LabelResponse
import os

class LabelCreator:
    def __init__(self):
        self.engines = {
            "fedex": FedExShipEngine(),
            "ups": UPSShipEngine(),
        }

    async def create_label(self, request: LabelRequest) -> LabelResponse:
        engine = self.engines.get(request.carrier)
        if not engine:
            raise ValueError("Unsupported carrier")

        label = await engine.create_label(request)

        # Fallback QR code generation
        if not label.native_qr_code_base64:
            label_url = label.label_url
            qr_output_path = f"static/labels/qr/{label.tracking_number}.png"
            generate_qr_code(label_url, qr_output_path)
            label.fallback_qr_code_url = f"/static/labels/qr/{label.tracking_number}.png"

        return label
