# ShipVox FedEx Ship API Tests

This directory contains test scripts for the FedEx Ship API integration in ShipVox. The tests are designed to verify the functionality of the label creation pipeline for various shipping scenarios.

## Test Cases

The following test cases are included:

- **SH0005**: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING
- **SH0006**: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING with Special Services
- **SH0007**: US to US, FEDEX_GROUND, YOUR_PACKAGING
- **SH0008**: US to US, FEDEX_2_DAY, YOUR_PACKAGING
- **SH0009**: US to US, FEDEX_EXPRESS_SAVER, YOUR_PACKAGING
- **SH0018**: US to Canada, INTERNATIONAL_PRIORITY, YOUR_PACKAGING
- **SH0019**: US to Mexico, INTERNATIONAL_ECONOMY, YOUR_PACKAGING
- **SH0203**: US to US, FEDEX_GROUND, YOUR_PACKAGING with COD
- **SH0262**: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING with Dry Ice
- **SH0439**: US to US, FEDEX_GROUND, YOUR_PACKAGING with Residential Delivery
- **SH0453**: US to US, FEDEX_GROUND, YOUR_PACKAGING with Hold at Location
- **SH0457**: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING with Email Notification
- **SH0460**: US to US, FEDEX_GROUND, YOUR_PACKAGING with Return Shipment
- **SH0464**: US to US, PRIORITY_OVERNIGHT, YOUR_PACKAGING with Dangerous Goods
- **SH0473**: US to US, FEDEX_GROUND, YOUR_PACKAGING with Multiple Packages

## Running the Tests

### Prerequisites

- Python 3.7 or higher
- Required packages: `requests`, `dotenv`
- FedEx API credentials in `.env` file
- ShipVox backend server running

### Running Individual Tests

To run an individual test case:

```bash
python SH0005_test.py
```

### Running All Tests

To run all test cases:

```bash
python run_all_tests.py
```

## Test Results

Each test will output:
- The request payload
- The response status code
- The tracking number
- The label URL
- QR code information
- Estimated delivery date

## Notes

- These tests use the ShipVox API endpoint (`http://localhost:8000/api/labels`) rather than calling the FedEx API directly.
- The tests assume that the ShipVox backend server is running on localhost port 8000.
- Some special services may not be fully implemented in the ShipVox backend yet.
- International shipments require customs information.
- Multiple package shipments may return multiple labels or a master label with child labels.

## Troubleshooting

If a test fails:
1. Check that the ShipVox backend server is running
2. Verify that your FedEx API credentials are correct in the `.env` file
3. Check the error message for details on what went wrong
4. Examine the ShipVox backend logs for more information
