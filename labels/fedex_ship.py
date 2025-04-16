import os
import base64
import httpx
import json
from datetime import datetime, timedelta
from pathlib import Path

from models.label_request import LabelRequest
from models.label_response import LabelResponse
from models.carriers.fedex import FedExAddress, FedExWeight, FedExDimensions
from auth.fedex_auth import FedExAuth

class FedExShipEngine:
    def __init__(self):
        self._auth = FedExAuth()
        self._base_url = os.getenv('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')
        self._account_number = os.getenv('FEDEX_ACCOUNT_NUMBER')
        self._client = httpx.AsyncClient()

        # Ensure static directories exist
        Path('static/labels').mkdir(parents=True, exist_ok=True)
        Path('static/labels/qr').mkdir(parents=True, exist_ok=True)

    async def create_label(self, request: LabelRequest) -> LabelResponse:
        """Create a shipping label using FedEx Ship API"""
        try:
            # Get authentication token
            token = await self._auth.get_token()

            # Prepare the ship request
            ship_request = self._prepare_ship_request(request)

            # Send request to FedEx API
            ship_url = f"{self._base_url}/ship/v1/shipments"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-locale": "en_US"
            }

            response = await self._client.post(
                ship_url,
                headers=headers,
                json=ship_request
            )

            # Handle response
            response.raise_for_status()
            response_data = response.json()

            # Print response for debugging
            print("FedEx API Response:")
            print(json.dumps(response_data, indent=2))

            # Extract tracking number and label data
            tracking_number = self._extract_tracking_number(response_data)
            label_data = self._extract_label_data(response_data)

            # Save label PDF to file
            label_path = f"static/labels/{tracking_number}.pdf"
            self._save_label_pdf(label_data, label_path)

            # Check for native QR code
            native_qr = self._extract_qr_code(response_data)

            # Estimate delivery date (could be extracted from response if available)
            estimated_delivery = datetime.now() + timedelta(days=3)  # Default estimate

            # Return label response
            return LabelResponse(
                tracking_number=tracking_number,
                label_url=f"/static/labels/{tracking_number}.pdf",
                native_qr_code_base64=native_qr,
                carrier="fedex",
                estimated_delivery=estimated_delivery
            )

        except httpx.HTTPError as e:
            # Handle HTTP errors
            error_msg = f"FedEx API error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            print(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            # Handle other errors
            error_msg = f"Error creating FedEx label: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)

    def _prepare_ship_request(self, request: LabelRequest) -> dict:
        """Prepare the FedEx ship request payload"""
        # Convert Address model to FedEx format
        shipper_address = FedExAddress(
            streetLines=[request.shipper.street],
            city=request.shipper.city,
            stateOrProvinceCode=request.shipper.state,
            postalCode=request.shipper.zip_code,
            countryCode=request.shipper.country
        )

        recipient_address = FedExAddress(
            streetLines=[request.recipient.street],
            city=request.recipient.city,
            stateOrProvinceCode=request.recipient.state,
            postalCode=request.recipient.zip_code,
            countryCode=request.recipient.country
        )

        # Convert Package model to FedEx format
        weight = FedExWeight(
            value=request.package.weight,
            units="LB"
        )

        dimensions = None
        if request.package.dimensions:
            dimensions = FedExDimensions(
                length=request.package.dimensions.length,
                width=request.package.dimensions.width,
                height=request.package.dimensions.height,
                units="IN"
            )

        # Build the request payload
        ship_request = {
            "accountNumber": {
                "value": self._account_number
            },
            "labelResponseOptions": "URL_ONLY",
            "requestedShipment": {
                "shipper": {
                    "address": shipper_address.model_dump(),
                    "contact": {
                        "personName": request.shipper.name,
                        "companyName": request.shipper.name,
                        "phoneNumber": "5555555555"  # Default phone number
                    }
                },
                "recipients": [{
                    "address": recipient_address.model_dump(),
                    "contact": {
                        "personName": request.recipient.name,
                        "companyName": request.recipient.name,
                        "phoneNumber": "5555555555"  # Default phone number
                    }
                }],
                "shipDatestamp": datetime.now().strftime("%Y-%m-%d"),
                "serviceType": request.service_type,
                "packagingType": "YOUR_PACKAGING",
                "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                "blockInsightVisibility": False,
                "shippingChargesPayment": {
                    "paymentType": "SENDER"
                },
                "labelSpecification": {
                    "labelFormatType": "COMMON2D",
                    "imageType": "PDF",
                    "labelStockType": "PAPER_85X11_TOP_HALF_LABEL"
                },
                "requestedPackageLineItems": [{
                    "weight": weight.model_dump(),
                    "groupPackageCount": 1
                }]
            }
        }

        # Add dimensions if available
        if dimensions:
            ship_request["requestedShipment"]["requestedPackageLineItems"][0]["dimensions"] = dimensions.model_dump()

        return ship_request

    def _extract_tracking_number(self, response_data: dict) -> str:
        """Extract tracking number from FedEx response"""
        try:
            # Navigate through the response to find the tracking number
            tracking_number = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("masterTrackingNumber")
            if not tracking_number:
                # Try alternative path for tracking number
                tracking_number = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("pieceResponses", [{}])[0].get("trackingNumber")

            if not tracking_number:
                raise ValueError("Tracking number not found in response")

            return tracking_number
        except (IndexError, KeyError, AttributeError) as e:
            raise ValueError(f"Error extracting tracking number: {str(e)}")

    def _extract_label_data(self, response_data: dict) -> str:
        """Extract label data from FedEx response"""
        try:
            # For URL_ONLY response, we need to download the label from the URL
            documents = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("pieceResponses", [{}])[0].get("packageDocuments", [])

            for doc in documents:
                # Check for different content types
                if doc.get("contentType") == "LABEL":
                    # Return the base64 content directly
                    return doc.get("docContent", "")
                elif doc.get("contentType") == "URL_ONLY" and doc.get("docType") == "PDF":
                    # Return the encoded label directly
                    return doc.get("encodedLabel", "")
                elif doc.get("url"):
                    # Download the label from the URL
                    label_url = doc.get("url")
                    print(f"Downloading label from URL: {label_url}")
                    response = httpx.get(label_url)
                    response.raise_for_status()
                    return base64.b64encode(response.content).decode('utf-8')

            # If we get here, we didn't find a label in the expected format
            # Let's try to find any document that might contain label data
            for doc in documents:
                if doc.get("encodedLabel"):
                    return doc.get("encodedLabel")
                elif doc.get("docContent"):
                    return doc.get("docContent")

            raise ValueError("Label data not found in response")
        except (IndexError, KeyError, AttributeError) as e:
            raise ValueError(f"Error extracting label data: {str(e)}")
        except httpx.HTTPError as e:
            raise ValueError(f"Error downloading label: {str(e)}")

    def _extract_qr_code(self, response_data: dict) -> str:
        """Extract QR code from FedEx response if available"""
        try:
            # Check if there's a QR code in the response
            documents = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("pieceResponses", [{}])[0].get("packageDocuments", [])

            for doc in documents:
                if doc.get("contentType") == "AUXILIARY" and doc.get("docType") == "QR_CODE":
                    return doc.get("docContent", "")

            return None  # No QR code found
        except (IndexError, KeyError, AttributeError):
            return None  # Error occurred, no QR code

    def _save_label_pdf(self, label_data: str, file_path: str) -> None:
        """Save base64 encoded label data as PDF file"""
        try:
            # Decode base64 data
            pdf_data = base64.b64decode(label_data)

            # Save to file
            with open(file_path, "wb") as f:
                f.write(pdf_data)
        except Exception as e:
            raise ValueError(f"Error saving label PDF: {str(e)}")
