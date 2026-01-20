# Lotus Approach Service Management System Documentation

Complete documentation for a Lotus Approach-based field service management and parts tracking system for an appliance repair business.

## Overview

This repository contains comprehensive documentation and code for a legacy Lotus Approach database system used to manage:
- Service call tickets and work orders
- Parts inventory across multiple locations (8,900+ parts)
- Supplier integration (Marcone parts distributor)
- Customer invoicing and payment processing
- Financial reporting by pay period

## Repository Contents

### Core Documentation

- **[Lotus_System_Comprehensive_Summary.md](Lotus_System_Comprehensive_Summary.md)** - Complete system documentation covering:
  - All 50+ APR database files and their purposes
  - File type explanations (APR, DBF, ADX)
  - Daily workflows for service operations
  - LotusScript automation and macros
  - Data relationships and field definitions
  - Technical implementation details

- **[Ticket_Creation_Lifecycle_and_Scripts.md](Ticket_Creation_Lifecycle_and_Scripts.md)** - Detailed documentation on ticket/call creation:
  - Complete 8-stage ticket lifecycle
  - Deep dive into the `dup` script (ticket duplication)
  - All 25+ focus navigation scripts
  - Step-by-step data entry workflows
  - Field validation and business rules
  - Behind-the-scenes automation
  - Complete LotusScript code reference

### Integration Code

- **[app.py](app.py)** - Flask web application for ServicePower ServiceDispatch API integration
- **[test_servicedispatch.py](test_servicedispatch.py)** - API testing utility
- **[TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md)** - Setup and testing instructions

### Database Files

- **`Lotus documentation/`** - Complete collection of:
  - 50+ APR database application files
  - 30+ DBF data files
  - ADX index files
  - LotusScript references and version notes
  - Database diagrams and field definitions

### ServicePower Documentation

- **`sp documentation/`** - Integration guides for:
  - Claims Retrieval API v1.2
  - Claims Submission API v1.10
  - Dispatch Web Service Interface v2.8
  - Request for Authorization Web Service v2.5

## System Architecture

### Technology Stack

**Database Layer:**
- Lotus Approach (legacy database application platform)
- dBase IV format (.DBF files) for data storage
- LotusScript for automation and business logic

**Web Integration:**
- Python 3 with Flask
- SOAP/XML for ServiceDispatch API
- REST/JSON for ServiceClaims API

**Network:**
- Multi-user access via shared network drive (Y:\Lotus)
- HTTPS connectivity to ServicePower endpoints

### Key Databases

1. **STATUSUPDATE.APR** - Main ticket/work order system (CUSTDATA.DBF)
2. **Partlog.APR** - Parts inventory tracking
3. **MARCONE ORDERS/RETURNS/CREDITS** - Supplier integration
4. **STOCK ONLY.APR** - Current inventory
5. **Payments.APR** - Payment records and financial tracking

## Business Operations

### Service Territory
- **Geographic coverage:** Nebraska (Omaha, Lincoln, Bellevue, Fremont) and Iowa (Council Bluffs)
- **Service locations:** 125+ documented locations
- **Business model:** Multi-location appliance repair company

### Workflow Overview

1. **Ticket Creation** - Customer brings device or calls for service
2. **Information Gathering** - Customer, device, and problem documentation
3. **Diagnosis & Repair** - Technician performs service
4. **Work Documentation** - Parts, labor, and charges recorded
5. **Invoice Generation** - Print customer invoice
6. **Payment Collection** - Process payment and record method
7. **Customer Pickup** - Device return and ticket closure
8. **Financial Reporting** - Bi-monthly Sales Journal reports (1st-14th, 15th-end)

## Key Features

### LotusScript Automation

**`dup` Script** - Core duplication logic for returning customers:
- Preserves customer information
- Clears device, service, parts, and payment fields
- Auto-sets dates (DATEIN = Today, DATEPROM = Today + 7)
- Critical for efficient data entry

**Focus Navigation Scripts** - 25+ scripts for keyboard-driven data entry:
- `FocMake`, `FocModel`, `FocSerial` - Device information
- `FocQ1-Q10` - Quick jump to quantity fields
- `FocSympt` - Service request entry

**Date Handling** - Automatic pay period navigation:
- `SetDates` - Auto-calculate current period
- `PrevBut` / `NextBut` - Navigate between periods

### Automatic Triggers

When parts are entered in a ticket:
1. **Partlog record created** with unique TIMEKEY (14-digit identifier)
2. **KEY field generated** for Marcone supplier linking
3. **Stock reduced** in STOCK ONLY.APR
4. **Location inventory updated** in DISTINCTLOCATIONS.APR
5. **Return eligibility checked** against MARCONE AVAILABLE RETURNS

### Unique Identifier: TIMEKEY

14-digit timestamp-based unique ID:
```
Last digit of year (1) +
Day of year (3) +
Hour (2) + Minute (2) + Second (2) +
Random (2)
```

Example: `50201234512345` = 2025-01-20 12:34:51.23

### Marcone Supplier Integration

**KEY Field** - Composite linking field:
```
KEY = COST + "  " + INVOICE + "  " + PART_NUM
```

Links Partlog to:
- MARCONE AVAILABLE RETURNS (return eligibility)
- MARCONE SALES AND CREDITS (financial reconciliation)

## Data Validation

### Date Validation (DATECOMPLT)
```
DATECOMPLT = '' OR
(DATECOMPLT <= Today() AND DATECOMPLT >= DATEIN)
```

Ensures completion date is:
- Empty (work not done), OR
- Not in future AND not before check-in

### Quantity Fields (Q1-Q11)
**Critical distinction:**
- Empty string `''` = no part used
- Zero `0` = different meaning in calculations
- The `dup` script explicitly sets quantities to `''`

## Installation & Setup

### Prerequisites
- Lotus Approach (for database access)
- Python 3.x (for web integration)
- Flask framework
- Access to ServicePower APIs (credentials required)

### Configuration
See [TEST_INSTRUCTIONS.md](TEST_INSTRUCTIONS.md) for:
- ServiceDispatch API setup
- Credential configuration
- Testing procedures

## Known Issues

1. **DATECOMPLT validation during duplication** - Can trigger errors when old completion date is before new check-in date
2. **Field linking to MARCONE AVAILABLE RETURNS** - Resolved with modified KEY formula (7/10/25)
3. **Part number resolution** - ResolvedPn field handles superseded part numbers

## Future Enhancements

- Improved location tagging system (LOCATION TAG EXPERIMENT.APR in development)
- MySQL integration (attempted connection to 192.168.1.30)
- Web-based interface expansion (Flask app foundation exists)

## File Structure

```
/
├── README.md
├── Lotus_System_Comprehensive_Summary.md
├── Ticket_Creation_Lifecycle_and_Scripts.md
├── app.py
├── test_servicedispatch.py
├── TEST_INSTRUCTIONS.md
├── Lotus documentation/
│   ├── STATUSUPDATE.APR
│   ├── Partlog.APR
│   ├── MARCONE *.APR
│   ├── *.DBF (data files)
│   ├── *.ADX (index files)
│   └── Documentation files
├── sp documentation/
│   └── Integration guides (PDF)
└── templates/
    └── index.html
```

## Contributing

This is documentation for a production system. Changes to LotusScript or database structure should be:
1. Tested in development environment
2. Documented in Version notes.txt
3. Backed up before deployment
4. Communicated to all users

## License

Documentation for internal business system. Not for redistribution.

## Contact

For questions about this documentation or the system, refer to the detailed markdown files or version notes in the Lotus documentation folder.

---

**Business Metrics:**
- 8,900+ parts tracked
- 125+ service locations
- 50+ APR database files
- Bi-monthly financial reporting (1st-14th, 15th-end of month)
- Multi-location operation in Nebraska and Iowa
