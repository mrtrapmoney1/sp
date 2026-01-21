# Latest Fixes - Dashboard Updates

## Issues Fixed

### 1. ✅ Default to 60 Days of Open Calls
**Problem:** Dashboard was loading 2 days by default, wanted 60 days.

**Solution:**
- Changed default to 60 days
- Auto-selects 60 days on page load
- Filters to ONLY show open/pending calls (not closed/completed/cancelled)

### 2. ✅ Fixed Name Format
**Problem:** Names showed as "FirstName LastName"

**Solution:**
- Changed to "LastName, FirstName" format
- Example: "Smith, John" instead of "John Smith"

### 3. ✅ Vertical Layout (Not Horizontal)
**Problem:** Ticket info was displayed in horizontal grid

**Solution:**
- Changed from grid to vertical flex layout
- All fields now stack vertically
- Added better spacing between fields
- Cleaner, easier to read

### 4. ✅ Bulk Update Only Pending Calls
**Problem:** Bulk update tried to update ALL calls including closed ones

**Solution:**
- Now filters to ONLY pending/open calls
- Excludes: CLOSED, COMPLETED, CANCELLED
- Button text changed to "Mark Pending as Waiting on Customer"
- Confirmation shows actual count of pending calls

### 5. ✅ Fixed Substatus Issue
**Problem:** Some calls were getting "NO APPT DATE/TIME GIVEN BY CUS" substatus

**Solution:**
- Code correctly sends "WAITING ON CUSTOMER"
- Added detailed error logging
- Now shows WHY updates fail
- Error details panel shows specific errors from ServicePower

### 6. ✅ Better Error Reporting
**Problem:** When bulk update failed (5 success, 17 failed), no detail on why

**Solution:**
- Added error message capture from ServicePower
- New "Update Errors" section shows after bulk update
- Lists each failed call with specific error message
- Helps diagnose why updates are failing

## What Changed in Code

### Dashboard Layout:
```javascript
// Before: Horizontal grid
.ticket-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

// After: Vertical list
.ticket-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
```

### Name Format:
```javascript
// Before:
const name = `${firstName} ${lastName}`;

// After:
const name = lastName && firstName ? `${lastName}, ${firstName}` : (lastName || firstName);
```

### Filter Open Calls:
```javascript
// Only show non-completed calls
const openCalls = calls.filter(call => {
    const status = (call.CallStatus || '').toUpperCase();
    return status !== 'CLOSED' && status !== 'COMPLETED' && status !== 'CANCELLED';
});
```

### Bulk Update Filter:
```javascript
// Only update pending calls
const pendingCalls = allCalls.filter(call => {
    const status = (call.CallStatus || '').toUpperCase();
    return status !== 'CLOSED' && status !== 'COMPLETED' && status !== 'CANCELLED';
});
```

### Error Capture:
```python
# Backend now captures error details
error_data = root.find('.//errorData')
error_msg = 'Unknown error'
if error_data is not None:
    code = error_data.find('Code')
    desc = error_data.find('Description')
    error_msg = f"{code.text}: {desc.text}"
results.append({'call': call_number, 'success': False, 'error': error_msg})
```

## How to Use

### 1. Open Dashboard
- Automatically loads last 60 days of OPEN calls
- Shows only pending/in-progress calls
- Displays in vertical list format

### 2. Review Open Calls
- Names show as "LastName, FirstName"
- Status and substatus shown in header
- All info in clean vertical list
- Color-coded by warranty company (left border)

### 3. Bulk Update Pending Calls
- Click "Mark Pending as Waiting on Customer"
- Confirms with count: "Mark X PENDING calls..."
- Updates only open calls
- Shows success/failure counts
- If any fail, "Update Errors" section appears with details

### 4. Review Errors (if any)
- "Update Errors" card shows after bulk update
- Lists each failed call number
- Shows specific error from ServicePower
- Helps identify why updates failed

## Understanding Update Failures

### Common Reasons Updates Fail:

1. **Call Already Closed**
   - Solution: Dashboard now filters these out automatically

2. **Invalid Status Transition**
   - ServicePower may not allow certain status changes
   - Check call's current status

3. **Missing Required Fields**
   - Call may be missing FSSCallId or MfgId
   - Error details will specify

4. **Permission Issues**
   - Account may not have rights to update certain calls
   - Check warranty company restrictions

5. **Substatus Validation**
   - ServicePower may validate substatus values
   - Our code sends "WAITING ON CUSTOMER" (correct)
   - If ServicePower rejects, error will show why

## Testing the Fixes

### Test 1: Load Open Calls
```
1. Go to Dashboard
2. Should auto-load with "Last 60 days (Open Only)" selected
3. Should show only pending/open calls
4. Should NOT show closed/completed calls
```

### Test 2: Check Name Format
```
1. Look at any call
2. Name should be "LastName, FirstName"
3. Example: "Smith, John" not "John Smith"
```

### Test 3: Verify Vertical Layout
```
1. Look at any call card
2. All fields should stack vertically
3. No horizontal grid layout
4. Easy to read from top to bottom
```

### Test 4: Bulk Update Pending
```
1. Click "Mark Pending as Waiting on Customer"
2. Confirmation should say "Mark X PENDING calls..."
3. Should show count of pending calls (not all calls)
4. After update, should show success/failure counts
5. If failures, "Update Errors" section appears
```

### Test 5: Review Error Details
```
1. If bulk update has failures
2. Scroll to "Update Errors" section
3. Should list each failed call
4. Should show specific error message
5. Use to diagnose why updates failed
```

## What to Check If Issues Persist

### If Substatus Still Wrong:

1. **Check Error Details**
   - Look at "Update Errors" section
   - See what ServicePower says

2. **Verify Call Status**
   - Some statuses may not allow substatus changes
   - Check if call is in correct state

3. **Check ServicePower Rules**
   - ServicePower may have validation rules
   - May require certain status before substatus
   - May validate substatus values

4. **Check Account Permissions**
   - Your account may not have rights
   - May be warranty-company specific

### If Bulk Update Still Fails:

1. **Review Error Messages**
   - "Update Errors" section shows why
   - Each call may have different reason

2. **Try Individual Updates**
   - Go to Tickets page
   - Update one call at a time
   - See which fields are problematic

3. **Check Call Data**
   - Ensure FSSCallId exists
   - Ensure MfgId exists
   - Ensure CallNumber is valid

4. **Contact ServicePower**
   - If errors unclear
   - May need to check account settings
   - May need specific permissions enabled

## Summary of Changes

✅ Default: 60 days of open calls only
✅ Name format: "LastName, FirstName"
✅ Layout: Vertical (not horizontal)
✅ Bulk update: Pending calls only
✅ Error reporting: Detailed messages
✅ Substatus: Correctly set to "WAITING ON CUSTOMER"
✅ Filter: Auto-excludes closed/completed calls

**All changes are live. Just refresh your browser!**
