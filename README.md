# ShipVox Backend

Shipping middleware API that provides a unified interface for rate comparison and label generation across multiple carriers (FedEx, UPS).

## Project Setup

### 📦 Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install requirements
pip install -r requirements.txt
```

### 🔑 Environment Configuration

Create a `.env` file in the root directory:

```env
# API Settings
PORT=8000
ENVIRONMENT=development

# Feature Flags
ENABLE_UPS=false

# FedEx Credentials
FEDEX_CLIENT_ID=your_client_id
FEDEX_CLIENT_SECRET=your_client_secret
FEDEX_API_URL=https://apis-sandbox.fedex.com

# UPS Credentials (when enabled)
UPS_CLIENT_ID=your_client_id
UPS_CLIENT_SECRET=your_client_secret
```

### 🛠 Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Rate Comparison Endpoint

**POST** `/api/get-rates`

Request body:
```json
{
  "originZip": "12345",
  "destinationZip": "67890",
  "weight": 10.5,
  "dimensions": {
    "length": 12,
    "width": 8,
    "height": 6
  },
  "pickupRequested": false
}
```

Response:
```json
{
  "cheapestOption": {
    "carrier": "FedEx",
    "service": "GROUND",
    "cost": 24.99,
    "transitDays": 3
  },
  "cheapestFastestOption": {
    "carrier": "UPS",
    "service": "2DA",
    "cost": 34.99,
    "transitDays": 2
  }
}
```

## 📂 Folder Structure

- `/auth`: OAuth management for carrier APIs
  - `fedex_auth.py`: FedEx OAuth implementation
  - `ups_auth.py`: UPS OAuth implementation (planned)
  - `base_auth.py`: Abstract authentication provider
  - `token_manager.py`: Token caching and refresh logic

- `/rates`: Rate request and comparison modules
  - `rate_service.py`: Main orchestration service
  - `rate_comparer.py`: Rate comparison logic
  - `fedex_rates.py`: FedEx rate engine
  - `ups_rates.py`: UPS rate engine (planned)
  - `service_normalizer.py`: Carrier service standardization

- `/labels`: Label creation modules (planned)
  - Label generation for selected carrier/service

- `/pickup`: Pickup scheduler modules (planned)
  - Carrier-specific pickup request handling

- `/utils`: Shared utilities
  - `exceptions.py`: Custom exception classes
  - `logging.py`: Logging configuration
  - `validation.py`: Input validation helpers

- `/data`: Static data and mappings
  - Service code mappings
  - Rate calculation tables
  - Carrier-specific configurations

## 🔄 Current Status

- ✅ Core rate comparison engine
- ✅ FedEx integration
- ✅ Service normalization
- ✅ Rate comparison logic
- 🚧 UPS integration (in progress)
- 📋 Label generation (planned)
- 📋 Pickup scheduling (planned)

## 🛠 Development

### Adding a New Carrier

1. Create auth provider in `/auth`
2. Implement rate engine in `/rates`
3. Add service mappings to `service_normalizer.py`
4. Update `rate_service.py` to include new carrier

### Running Tests

```bash
pytest tests/
```

## 📝 License

[License details here]
