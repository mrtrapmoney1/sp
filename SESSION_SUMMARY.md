# ServiceDispatch Session Summary

**Date:** January 26, 2026
**Project:** ServiceDispatch - Flask-based service call management application

---

## Project Overview

ServiceDispatch is a web application for managing service calls that integrates with:
- **ServicePower SOAP API** - External service call management system
- **Lotus Approach** - Legacy dBase IV (.DBF) database system

### Tech Stack
- **Backend:** Flask 3.0+, SQLAlchemy, PostgreSQL
- **Frontend:** Jinja2 templates, HTMX, vanilla JavaScript
- **Data:** ServicePower SOAP API (raw XML), DBF files via dbfread/pandas

---

## Work Completed This Session

### 1. Fixed ASCII Encoding Error
**Problem:** `'ascii' codec can't decode byte 0xa8 in position 46` when loading dashboard

**Solution:** Updated `app/services/servicepower.py`:
- Added UTF-8 encoding handling in `parse_calls_from_response()` function
- Set explicit `response.encoding = 'utf-8'` on HTTP responses
- Handles non-ASCII characters in SOAP responses gracefully

### 2. Replaced "Scheduled" with "Cancelled" Filter
**File:** `app/templates/pages/index.html`

Changed:
- Status dropdown option: `SCHEDULED` → `CANCELLED`
- Stat card: `stat-scheduled` → `stat-cancelled` (now uses `stat-card--danger` styling)
- Filter tag: `SCHEDULED` → `CANCELLED`
- JavaScript functions `updateStats()` and `updateFilterTags()` now count `CANCEL` instead of `SCHEDUL`

### 3. Created PDF/Excel Import Feature
Allows importing ServicePower PDF exports (like SA-1831469.pdf) and converting to Lotus DBF format.

**New Files Created:**

#### `app/api/imports.py`
API endpoints:
- `POST /api/import/pdf` - Parse ServicePower PDF, extract call data
- `POST /api/import/excel` - Parse Excel/CSV files
- `POST /api/import/export-dbf` - Export to Lotus-compatible DBF

Key functions:
- `parse_servicepower_pdf()` - Extracts fields from PDF using regex patterns
- `parse_excel_import()` - Maps Excel columns to Lotus fields
- `create_lotus_dbf()` - Creates dBase IV DBF with exact 21-field Lotus structure

#### `app/templates/pages/import.html`
Import page with:
- PDF upload zone (drag-and-drop)
- Excel/CSV upload zone
- Extracted data preview
- Export to Lotus DBF button
- Field mapping reference

**Updated Files:**
- `app/api/__init__.py` - Added `imports_bp` export
- `app/__init__.py` - Registered `imports_bp` blueprint at `/api`
- `app/views/main.py` - Added `/import` route
- `app/templates/layouts/base.html` - Added "Import" nav link
- `requirements.txt` - Added `pdfplumber>=0.10.0`, `openpyxl>=3.1.0`

---

## Lotus DBF Field Structure (21 fields)

The exact field order required for Lotus import:

| Field | Type | Length | Description |
|-------|------|--------|-------------|
| INVOICE | C | 10 | Invoice number |
| LASTNAME | C | 25 | Customer last name |
| FIRSTNAME | C | 15 | Customer first name |
| ADDRESS | C | 40 | Street address |
| CITY | C | 20 | City |
| STATE | C | 2 | State (2 letters) |
| ZIP | C | 10 | ZIP code |
| PHONE | C | 15 | Primary phone |
| PHONE2 | C | 15 | Alt phone |
| LOCATION | C | 10 | Service location |
| SERVICEREQ | C | 250 | Service request/problem |
| MAKE | C | 20 | Brand/manufacturer |
| TYP | C | 20 | Product type |
| MODEL | C | 25 | Model number |
| SERIAL | C | 25 | Serial number |
| DATEIN | C | 10 | Date received |
| DATEPUR | C | 10 | Purchase date |
| BTADDRESS | C | 20 | ServicePower call number (SA-*) |
| ACCESSOR | C | 50 | Warranty type (IW/SC/OW) |
| TICLOC | C | 10 | Ticket location |
| DLRINVOICE | C | 20 | Case/dealer invoice |

---

## ServicePower API Notes

### Undocumented 2-Day Query Limit
The API silently fails for date ranges > 2 days. Solution implemented:
- `get_calls()` auto-splits large ranges into 2-day chunks
- Deduplicates results by `CallNumber`
- Continues processing if one chunk fails

### API Field Typos (must use exactly)
- `ProbelmDesc` (not ProblemDescription)
- `MobelNo` (not ModelNo)
- `EmaiIld` (not EmailId)
- `Phone2 = "0"` means empty

### Environments
```python
SERVICEPOWER_ENVIRONMENTS = {
    'staging_na': 'https://fssstag.servicepower.com/sms/services/SPDService',
    'staging_eu': 'https://fss-stg.hostedservicepower.eu/sms/services/SPDService',
    'production_na': 'https://fss.servicepower.com/sms/services/SPDService',
    'production_eu': 'https://fss.servicepower.eu/sms/services/SPDService',
}
```

---

## Project Structure

```
/mnt/c/Users/metro/sp/
├── app/
│   ├── __init__.py          # Flask factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions (db, etc.)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Login/logout endpoints
│   │   ├── calls.py         # Service calls CRUD
│   │   ├── export.py        # DBF export
│   │   ├── imports.py       # NEW: PDF/Excel import
│   │   └── parts.py         # Parts lookup
│   ├── services/
│   │   └── servicepower.py  # SOAP client (raw XML)
│   ├── views/
│   │   └── main.py          # Page routes
│   └── templates/
│       ├── layouts/
│       │   └── base.html    # Main layout with nav
│       ├── pages/
│       │   ├── index.html   # Dashboard
│       │   ├── import.html  # NEW: Import page
│       │   ├── login.html
│       │   ├── map.html
│       │   ├── parts.html
│       │   └── ...
│       └── components/
├── data/
│   └── lotus-database/      # DBF files
├── static/
│   └── css/
├── requirements.txt
├── run.py
└── CLAUDE.md                # Project instructions
```

---

## Default Credentials

Pre-filled on login page:
- **User ID:** MET11106
- **Servicer Account:** MET11106
- **Environment:** production_na

---

## Dependencies to Install

```bash
pip install pdfplumber openpyxl
```

Or full install:
```bash
pip install -r requirements.txt
```

---

## Known Issues / TODOs

1. **PDF Parsing:** The regex patterns in `parse_servicepower_pdf()` are based on SA-1831469.pdf format. May need adjustment for other PDF layouts.

2. **Excel Column Mapping:** The column name mappings in `parse_excel_import()` cover common variations but may need expansion.

3. **Invoice Auto-generation:** The INVOICE field is currently left empty for imported calls. Lotus may auto-generate this.

---

## Key Files Modified This Session

1. `app/services/servicepower.py` - Encoding fix
2. `app/templates/pages/index.html` - Scheduled→Cancelled
3. `app/api/imports.py` - NEW
4. `app/templates/pages/import.html` - NEW
5. `app/api/__init__.py` - Added imports_bp
6. `app/__init__.py` - Registered imports_bp
7. `app/views/main.py` - Added /import route
8. `app/templates/layouts/base.html` - Added Import nav link
9. `requirements.txt` - Added pdfplumber, openpyxl

---

## Running the Application

```bash
cd /mnt/c/Users/metro/sp
pip install -r requirements.txt
python run.py
```

Then open http://localhost:5000
