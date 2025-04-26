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
        self._base_url = os.environ.get('FEDEX_API_URL', 'https://apis-sandbox.fedex.com')
        self._account_number = '740561073'  # Hardcoded for testing
        self._client = httpx.AsyncClient()

        # Ensure static directories exist
        Path('static/labels').mkdir(parents=True, exist_ok=True)
        Path('static/labels/qr').mkdir(parents=True, exist_ok=True)

    async def create_label(self, request: LabelRequest) -> LabelResponse:
        """Create a shipping label using FedEx Ship API"""
        try:
            # Print request for debugging
            print("Label Request:")
            print(f"Carrier: {request.carrier}")
            print(f"Service Type: {request.service_type}")
            print(f"Special Services: {request.special_services}")

            # Get authentication token
            token = await self._auth.get_token()

            # Prepare the ship request
            ship_request = self._prepare_ship_request(request)

            # Print ship request for debugging
            print("FedEx Ship Request:")
            print(json.dumps(ship_request, indent=2))

            # Send request to FedEx API
            ship_url = f"{self._base_url}/ship/v1/shipments"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-locale": "en_US"
            }

            try:
                response = await self._client.post(
                    ship_url,
                    headers=headers,
                    json=ship_request,
                    timeout=30.0  # Add timeout
                )

                # Print response status for debugging
                print(f"FedEx API Response Status: {response.status_code}")

                # Get response data
                response_text = response.text
                print(f"FedEx API Response Text: {response_text}")

                # Handle response
                if response.status_code == 200:
                    response_data = response.json()

                    # Print response for debugging
                    print("FedEx API Response:")
                    print(json.dumps(response_data, indent=2))
                else:
                    # Try to parse error response
                    try:
                        error_data = response.json()
                        error_message = json.dumps(error_data)
                    except:
                        error_message = response_text if response_text else f"HTTP Error: {response.status_code}"

                    print(f"FedEx API Error: {error_message}")
                    raise ValueError(f"FedEx API error: {error_message}")
            except httpx.TimeoutException:
                print("FedEx API request timed out")
                raise ValueError("FedEx API request timed out")
            except httpx.RequestError as e:
                print(f"FedEx API request error: {str(e)}")
                raise ValueError(f"FedEx API request error: {str(e)}")

            # Extract tracking number and label data
            tracking_number = self._extract_tracking_number(response_data)
            label_data = self._extract_label_data(response_data)

            # Generate QR code for tracking
            qr_code_path = f"/static/labels/qr/{tracking_number}.png"

            # Estimate delivery date based on service type
            estimated_delivery = self._calculate_estimated_delivery(request.service_type)

            # Return label response
            return LabelResponse(
                tracking_number=tracking_number,
                label_url=label_data["url"],
                carrier="fedex",
                service_type=request.service_type,
                estimated_delivery=estimated_delivery,
                native_qr_code_base64=None,  # FedEx doesn't provide a native QR code
                fallback_qr_code_url=qr_code_path
            )

        except ValueError as e:
            # Pass through ValueError (which includes our FedEx API errors)
            print(f"Error: {str(e)}")
            raise
        except Exception as e:
            # Handle other errors
            error_msg = f"Error creating FedEx label: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
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

        # Get packaging type
        packaging_type = getattr(request.package, 'packaging_type', "YOUR_PACKAGING")

        # Check if model_dump method exists, otherwise use dict() method
        if hasattr(shipper_address, 'model_dump'):
            shipper_address_dict = shipper_address.model_dump()
            recipient_address_dict = recipient_address.model_dump()
            weight_dict = weight.model_dump()
        else:
            # For older versions of Pydantic
            shipper_address_dict = shipper_address.dict()
            recipient_address_dict = recipient_address.dict()
            weight_dict = weight.dict()

        # Build the request payload
        ship_request = {
            "accountNumber": {
                "value": self._account_number
            },
            "labelResponseOptions": "URL_ONLY",
            "requestedShipment": {
                "shipper": {
                    "address": shipper_address_dict,
                    "contact": {
                        "personName": request.shipper.name,
                        "companyName": request.shipper.company if hasattr(request.shipper, 'company') and request.shipper.company else request.shipper.name,
                        "phoneNumber": request.shipper.phone if hasattr(request.shipper, 'phone') and request.shipper.phone else "5555555555"
                    }
                },
                "recipients": [{
                    "address": recipient_address_dict,
                    "contact": {
                        "personName": request.recipient.name,
                        "companyName": request.recipient.company if hasattr(request.recipient, 'company') and request.recipient.company else request.recipient.name,
                        "phoneNumber": request.recipient.phone if hasattr(request.recipient, 'phone') and request.recipient.phone else "5555555555"
                    }
                }],
                "shipDatestamp": datetime.now().strftime("%Y-%m-%d"),
                "serviceType": request.service_type,
                "packagingType": packaging_type,
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
                    "weight": weight_dict,
                    "groupPackageCount": 1
                }]
            }
        }

        # Add dimensions if available
        if dimensions:
            if hasattr(dimensions, 'model_dump'):
                dimensions_dict = dimensions.model_dump()
            else:
                dimensions_dict = dimensions.dict()
            ship_request["requestedShipment"]["requestedPackageLineItems"][0]["dimensions"] = dimensions_dict

        # Add special services if available
        if request.special_services:
            special_services = {
                "specialServiceTypes": []
            }

            # Add signature option if specified
            if request.special_services.signature_option:
                special_services["signatureOptionType"] = request.special_services.signature_option

            # Add Saturday delivery if requested
            if request.special_services.saturday_delivery:
                special_services["specialServiceTypes"].append("SATURDAY_DELIVERY")

            # Add Sunday delivery if requested
            if request.special_services.sunday_delivery:
                special_services["specialServiceTypes"].append("SUNDAY_DELIVERY")

            # Add residential delivery if requested
            if request.special_services.residential_delivery:
                # Make a copy of the address dictionary
                address_dict = ship_request["requestedShipment"]["recipients"][0]["address"]
                # Add the residential flag
                address_dict["residential"] = True
                # Update the address in the ship_request
                ship_request["requestedShipment"]["recipients"][0]["address"] = address_dict

            # Add hold at location if requested
            if request.special_services.hold_at_location:
                special_services["specialServiceTypes"].append("HOLD_AT_LOCATION")

            # Add dry ice if requested
            if request.special_services.dry_ice:
                special_services["specialServiceTypes"].append("DRY_ICE")

            # Add dangerous goods if requested
            if request.special_services.dangerous_goods:
                special_services["specialServiceTypes"].append("DANGEROUS_GOODS")

            # Add priority alert if requested
            if request.special_services.priority_alert:
                special_services["specialServiceTypes"].append("PRIORITY_ALERT")

            # Only add special services if there are any
            if special_services["specialServiceTypes"] or "signatureOptionType" in special_services:
                ship_request["requestedShipment"]["specialServicesRequested"] = special_services

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

    def _extract_label_data(self, response_data: dict) -> dict:
        """Extract label data from FedEx response"""
        try:
            # For URL_ONLY response, we get a URL to the label
            documents = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("pieceResponses", [{}])[0].get("packageDocuments", [])

            for doc in documents:
                if doc.get("url"):
                    # Return the URL directly
                    return {"url": doc.get("url")}
                elif doc.get("encodedLabel"):
                    # For encoded labels, save to a file and return the file path
                    tracking_number = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("masterTrackingNumber")
                    if not tracking_number:
                        tracking_number = response_data.get("output", {}).get("transactionShipments", [{}])[0].get("pieceResponses", [{}])[0].get("trackingNumber")

                    if not tracking_number:
                        raise ValueError("Tracking number not found in response")

                    # Save the encoded label to a file
                    label_path = f"static/labels/{tracking_number}.pdf"
                    with open(label_path, "wb") as f:
                        f.write(base64.b64decode(doc.get("encodedLabel")))

                    # Return the file path
                    return {"url": f"/static/labels/{tracking_number}.pdf"}

            # If we get here, we didn't find a label URL or encoded label
            raise ValueError("Label data not found in response")
        except (IndexError, KeyError, AttributeError) as e:
            raise ValueError(f"Error extracting label data: {str(e)}")
        except httpx.HTTPError as e:
            raise ValueError(f"Error downloading label: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing label data: {str(e)}")

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

    def _calculate_estimated_delivery(self, service_type: str) -> datetime:
        """Calculate estimated delivery date based on service type"""
        today = datetime.now()

        # Add days based on service type
        if service_type == "FEDEX_GROUND":
            # 3-5 business days
            return today + timedelta(days=5)
        elif service_type == "FEDEX_EXPRESS_SAVER":
            # 3 business days
            return today + timedelta(days=3)
        elif service_type == "FEDEX_2_DAY" or service_type == "FEDEX_2_DAY_AM":
            # 2 business days
            return today + timedelta(days=2)
        elif service_type == "STANDARD_OVERNIGHT" or service_type == "PRIORITY_OVERNIGHT" or service_type == "FIRST_OVERNIGHT":
            # Next business day
            return today + timedelta(days=1)
        else:
            # Default to 3 business days
            return today + timedelta(days=3)
