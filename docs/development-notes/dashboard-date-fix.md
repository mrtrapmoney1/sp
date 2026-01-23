# Dashboard Enhancements - January 23, 2026

## Summary

Enhanced the dashboard (`templates/pages/index.html`) with real-time date handling, ticket selection, export to DBF, and bulk status updates.

## Issues Identified & Fixed

1. **End date was editable** - Users could change the end date, causing outdated data
2. **Default range was "Today" (0 days)** - Should default to 7 days for practical use
3. **Date format display** - Needed MM-DD-YYYY format for readability
4. **No debug logging** - Couldn't trace API calls to ServicePower
5. **Login validation** - Wrong credentials could appear successful
6. **No ticket selection** - Couldn't select multiple tickets for actions
7. **No export feature** - Couldn't export tickets to Lotus DBF format
8. **No update feature** - Couldn't update ticket status from dashboard

## Changes Made

### 1. End Date Always Real-Time Today

- End date input is now **read-only** (`readonly` attribute)
- End date is automatically updated to today's date every time:
  - Page loads
  - Quick select button is clicked
  - Start date is changed
  - Fetch Calls button is clicked
- Label updated to "End Date (Today)" for clarity

### 2. Default 7-Day Range

- Changed default active button from "Today" to "7 Days"
- Start date now defaults to 7 days ago on page load

### 3. Date Format Display

- Added display divs showing dates in **MM-DD-YYYY** format
- HTML date inputs still use YYYY-MM-DD (required for HTML5 date input)
- Backend converts to ServicePower SOAP format: `mm/dd/yyyy HH24:mi:ss`

### 4. Debug Logging (app.py)

Added comprehensive logging to trace API calls:

```python
# Log file: servicepower_debug.log
# Logs include:
# - API requests (dates, user, environment)
# - SOAP request body (password masked)
# - HTTP response status and length
# - Parse results (success/error, call count)
# - Authentication attempts
# - Bulk update operations
```

### 5. Improved Login Validation

- Enhanced login endpoint to detect authentication errors
- Checks for auth-related keywords in error messages
- Logs all login attempts for debugging
- Returns count of calls found on successful login

### 6. Ticket Selection

- Added checkboxes to each ticket card
- "Select All" checkbox in toolbar
- Visual indication of selected tickets (highlighted border/background)
- Selection count display

### 7. Export to DBF

- "Export to DBF" button in toolbar
- Exports selected tickets to Lotus-compatible DBF format
- Maps ServicePower fields to Lotus CUSTDATA fields
- Auto-generates invoice numbers from call numbers

### 8. Bulk Status Update

- "Update Status" button in toolbar
- Modal dialog to select new status and sub-status
- Supported statuses: ACCEPTED, OPEN, COMPLETED, REJECTED, RESCHEDULED, CANCELED
- Supported sub-statuses: WAITING ON CUSTOMER, WAITING ON PART, SCHEDULED, IN PROGRESS, ON HOLD, NEEDS AUTHORIZATION
- Auto-refreshes call list after update

## Technical Details

### Date Flow

```
User Interface (HTML Date Input)
    Format: YYYY-MM-DD (e.g., "2026-01-16")
    Display: MM-DD-YYYY (e.g., "01-16-2026")
           |
           v
JavaScript (loadCalls)
    Sends: { from_date: "2026-01-16", to_date: "2026-01-23" }
           |
           v
Flask Backend (app.py - fetch_calls)
    Converts: from_datetime = "01/16/2026 00:00:00"
              to_datetime = "01/23/2026 23:59:59"
           |
           v
ServicePower SOAP API
    Receives: <FromDateTime>01/16/2026 00:00:00</FromDateTime>
              <ToDateTime>01/23/2026 23:59:59</ToDateTime>
```

### New JavaScript Functions

```javascript
formatDateDisplay(date)           // Converts Date to "MM-DD-YYYY" string
updateEndDateToToday()            // Sets end date to current real-time date
toggleTicketSelection(index)      // Toggle single ticket selection
toggleSelectAll()                 // Select/deselect all tickets
updateSelectionUI()               // Update checkboxes and action buttons
exportSelected()                  // Export selected tickets to DBF
showUpdateModal()                 // Open update status modal
closeUpdateModal()                // Close update status modal
updateSelectedCalls()             // Send bulk update request
```

### ServicePower API Reference

#### getCallInfoSearch Parameters

| Parameter | Format | Example |
|-----------|--------|---------|
| FromDateTime | mm/dd/yyyy HH24:mi:ss | 01/16/2026 00:00:00 |
| ToDateTime | mm/dd/yyyy HH24:mi:ss | 01/23/2026 23:59:59 |

#### updateCallInfoObj Parameters

| Parameter | Description |
|-----------|-------------|
| CallNumber | The call number to update |
| MfgId | Manufacturer ID |
| FSSCallId | FSS Call ID |
| CallStatus | New status (ACCEPTED, OPEN, etc.) |
| CallSubStatus | New sub-status |

### Endpoints

- **Production NA**: `https://fss.servicepower.com/sms/services/SPDService`
- **Staging NA**: `https://fssstag.servicepower.com/sms/services/SPDService`

### Lotus DBF Field Mapping

| ServicePower Field | Lotus Field | Max Length |
|-------------------|-------------|------------|
| ConsumerInfo_ConsumerLastName | LASTNAME | 25 |
| ConsumerInfo_ConsumerFirstName | FIRSTNAME | 15 |
| ConsumerInfo_ConsumerAddress1 | ADDRESS | 25 |
| ConsumerInfo_PostcodeLevel3 | CITY | 30 |
| ConsumerInfo_PostcodeLevel1 | STATE | 2 |
| ConsumerInfo_Postcode | ZIP | 5 |
| ConsumerInfo_Phone1 | PHONE | 12 |
| ConsumerInfo_Phone2 | PHONE2 | 12 |
| ProbelmDesc | SERVICEREQ | 250 |
| ProductInfo_SPBrandDesc | MAKE | 15 |
| ProductInfo_SPProductDesc | TYP | 15 |
| ProductInfo_MobelNo | MODEL | 20 |
| ProductInfo_SerialNo | SERIAL | 26 |
| CallNumber | BTADDRESS, DLRINVOICE | 30, 17 |

## Files Modified

- `/templates/pages/index.html` - Dashboard with all new features
- `/app.py` - Backend API with logging and improved validation

## Related Files

- `/templates/pages/map.html` - Map view (uses preset days only, different pattern)
- `/data/lotus-database/CUSTDATA.dbf` - Target Lotus database format

## Debug Log Location

```
/mnt/c/Users/metro/sp/servicepower_debug.log
```

## Testing Notes

1. **Date Handling**
   - Open dashboard
   - Verify end date shows today's date and is not editable
   - Verify start date shows 7 days ago by default
   - Click different quick select buttons - verify dates update correctly
   - Click "Fetch Calls" - verify tickets load
   - Manually change start date - verify end date stays as today

2. **Ticket Selection**
   - Load calls and verify checkboxes appear
   - Click individual checkboxes - verify selection count updates
   - Click "Select All" - verify all tickets selected
   - Verify action buttons enable/disable based on selection

3. **Export**
   - Select one or more tickets
   - Click "Export to DBF"
   - Verify DBF file downloads
   - Open in Lotus Approach to verify format

4. **Update Status**
   - Select one or more tickets
   - Click "Update Status"
   - Select new status and sub-status
   - Click "Update Calls"
   - Verify success message and calls refresh

5. **Debug Logging**
   - Check `servicepower_debug.log` for API traces
   - Verify dates being sent to ServicePower
   - Check for any authentication errors

---

*Last Updated: January 23, 2026*
