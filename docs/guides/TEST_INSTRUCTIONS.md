# ServiceDispatch API Test Script

## Overview

This test script validates authentication and database connectivity for the ServiceDispatch SPD Servicer Interface based on the Integration Guide v2.8.

## What It Tests

1. **Connectivity Test**: Verifies basic HTTPS connection to ServiceDispatch endpoints
2. **Authentication Test**: Validates user credentials using the getCallInfo API
3. **Database Query Test**: Tests actual data retrieval from the ServiceDispatch database

## Prerequisites

- Python 3.6 or higher
- `requests` library (install with: `pip install requests`)
- Valid ServiceDispatch credentials from your invitation email

## Credentials Required

You will need the following information from your ServiceDispatch invitation emails:

1. **User ID** (10 characters max)
   - Provided in the welcome email

2. **Password** (10 characters max)
   - Provided in the temporary password email
   - You may have changed this in the web interface

3. **Servicer Account Number** (10 characters max)
   - Your unique servicer account identifier

## Environments

The script supports four environments:

- **Staging - North America**: `https://fssstag.servicepower.com`
- **Staging - Europe**: `https://fss-stg.hostedservicepower.eu`
- **Production - North America**: `https://fss.servicepower.com`
- **Production - Europe**: `https://fss.servicepower.eu`

**Note**: Always test in Staging first before using Production credentials.

## Installation

1. Ensure Python 3 is installed:
   ```bash
   python3 --version
   ```

2. Install required dependencies:
   ```bash
   pip install requests
   ```

## Usage

### Interactive Mode

Run the script without arguments for interactive prompts:

```bash
python3 test_servicedispatch.py
```

You will be prompted for:
- User ID
- Password
- Servicer Account Number
- Environment selection

### Programmatic Usage

You can also import and use the tester class in your own code:

```python
from test_servicedispatch import ServiceDispatchTester

tester = ServiceDispatchTester(
    user_id="YOUR_USER_ID",
    password="YOUR_PASSWORD",
    servicer_account="YOUR_ACCOUNT",
    environment="staging_na"
)

# Run all tests
all_passed = tester.run_all_tests()

# Or run individual tests
success, message = tester.test_connectivity()
success, message = tester.test_authentication()
success, message = tester.test_database_query()
```

## Expected Output

### Successful Test Run

```
╔══════════════════════════════════════════════════════════╗
║  ServiceDispatch Authentication & Connection Test        ║
║  Based on Integration Guide v2.8                         ║
╚══════════════════════════════════════════════════════════╝

============================================================
ServiceDispatch API Test Suite
Environment: staging_na
URL: https://fssstag.servicepower.com/sms/services/SPDService
============================================================

============================================================
TEST 1: Basic Connectivity (getTestService)
============================================================
Connecting to: https://fssstag.servicepower.com/sms/services/SPDService
Response Status: 200
✓ Connection successful

============================================================
TEST 2: Authentication
============================================================
User ID: TESTUSER1
Servicer Account: ACC0001
Date Range: 01/08/2026 00:00:00 to 01/15/2026 23:59:59
✓ Authentication successful
✓ No call records found (but authentication worked)

============================================================
TEST 3: Database Query (getCallInfo)
============================================================
Querying calls from 12/16/2025 00:00:00 to 01/15/2026 23:59:59
✓ Database query successful
  No call records found in date range

============================================================
TEST SUMMARY
============================================================
✓ PASS: Connectivity
         Connectivity test passed
✓ PASS: Authentication
         Authentication successful
✓ PASS: Database Query
         Query successful but no records found
============================================================
✓ All tests passed successfully
```

## Common Error Codes

Based on Section 14.1 of the Integration Guide:

| Code | Description |
|------|-------------|
| SP000 | No records found (not an error) |
| SP002 | User ID does not exist in the system |
| SP003 | Password can't be null or blank |
| SP004 | Servicer account does not exist in the system |
| SP005 | User authentication failed |

## Troubleshooting

### Connection Errors

**Problem**: Cannot connect to endpoint
- Check your internet connection
- Verify firewall settings allow HTTPS outbound connections
- Ensure you're using the correct environment URL

**Problem**: HTTP 401/403 errors
- Verify your credentials are correct
- Check if your password has been changed via the web interface
- Ensure you're using the correct servicer account number

### Authentication Failures

**Error SP005**: Authentication Failed
- Double-check your User ID and Password
- Passwords are case-sensitive
- Verify you haven't exceeded 10 characters for any credential

**Error SP004**: Servicer Account Not Found
- Confirm your servicer account number
- Check if you're using the correct environment (staging vs production)

**Error SP002**: User ID Not Found
- Verify the User ID from your invitation email
- Ensure you're testing against the correct environment

### No Data Retrieved

If authentication succeeds but no call data is returned:
- This is normal if no jobs have been assigned to your account
- Try querying a wider date range
- Verify with your ServicePower contact that test data exists

## API Documentation Reference

This script implements the following APIs from the Integration Guide:

- **getTestService**: Basic connectivity test (Section 6.1)
- **getCallInfo**: Retrieve job information (Section 7)
  - Authentication using UserInfo object (Section 5.1)
  - Error handling (Section 5.3)
  - Response parsing (Section 7.4)

## Security Notes

- Never commit credentials to version control
- Use environment variables for production deployments
- Passwords are transmitted via HTTPS (SSL/TLS)
- Test in staging environment first
- Rotate passwords regularly

## Next Steps

After successful authentication testing:

1. **Review the Integration Guide** for available APIs:
   - `getCallAttributes` - Extended call information
   - `getProductCoverage` - Warranty information
   - `getCallAddresses` - Address details
   - `updateCallInfo` - Update job status
   - `updateTechInfo` - Manage technicians
   - `updateTechCapacity` - Update technician availability

2. **Implement Job Workflow**:
   - Schedule `getCallInfo` to run regularly
   - Process job assignments
   - Update job status with `updateCallInfo`
   - Handle parts and completion

3. **Error Handling**:
   - Implement retry logic for transient failures
   - Log all API interactions
   - Monitor for authentication expiry

## Support

For ServiceDispatch support:
- **Phone**: +44 (0)844 811 3302
- **Email**: support@servicepower.com
- **Hours**: Monday-Friday 9:00am - 5:30pm GMT

## Version

Script Version: 1.0
Integration Guide: v2.8 (18 April 2025)
