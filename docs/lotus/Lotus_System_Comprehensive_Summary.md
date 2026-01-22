# Lotus Approach System - Comprehensive Documentation Summary

## System Overview

The Lotus Approach system is a complete field service management and parts tracking application for an appliance repair business operating in Nebraska and Iowa (Omaha, Lincoln, Council Bluffs, Bellevue, Fremont, and surrounding areas).

**Primary Functions:**
- Service call ticket management and work orders
- Parts inventory tracking across multiple locations
- Customer invoicing and payment processing
- Supplier integration (primarily Marcone parts distributor)
- Financial reporting by pay period (bi-monthly: 1st-14th, 15th-end of month)

**Network Location:** `Y:\Lotus`

**Business Metrics:**
- 8,900+ parts tracked in inventory
- 125+ service locations
- Multi-location service company
- Primary supplier: Marcone (appliance parts distributor)
- Inventory tracked in 10% increment buckets by location

---

## File Types and Technical Structure

### APR Files (Approach Database Applications)
**What they are:** Complete database applications created in Lotus Approach

**Components within APR files:**
- Forms (data entry screens)
- Views (data display layouts)
- Reports (formatted printouts)
- Scripts (LotusScript macros for automation)
- Data storage layer

**Quantity:** 50+ APR files in the system

**Think of them as:** Self-contained mini-applications for specific business functions

**Key examples:**
- `STATUSUPDATE.APR` - Main ticketing system
- `Partlog.APR` - Parts tracking
- `MARCONE ORDERS.APR` - Supplier order management
- `STOCK ONLY.APR` - Current inventory
- `Payments.APR` - Payment records

### DBF Files (Database Format - Raw Data Storage)
**What they are:** The actual data tables in dBase IV format (industry standard)

**Relationship to APR:** APR files are the "application layer" that sits on top of DBF files for user interaction

**Format:** Field-based records (like spreadsheet rows)

**Key examples:**
- `CUSTDATA.DBF` - Customer service tickets (underlying data for STATUSUPDATE.APR)
- `Partlog.DBF` - Parts records
- `Marcone orders.dbf` - Supplier orders
- `Subs.dbf` - Substitute parts

**Why both exist:**
- APR = Application interface + forms + views + scripts + business logic
- DBF = Raw data storage (can be accessed by other tools)

### ADX Files (Index Files)
**What they are:** Binary index files for fast database lookups

**Created by:** Lotus Approach automatically when you index fields

**Purpose:** Speed up searches (finding part numbers, invoices, customer names quickly)

**Relationship:** One-to-one with indexed APR/DBF combinations

**User interaction:** Automatically managed by Approach - no manual editing needed

**Performance impact:** Critical for large datasets (8,900+ parts)

---

## Core Databases and Their Purposes

### 1. STATUSUPDATE.APR (Main Ticket/Work Order System)
**Underlying file:** `CUSTDATA.DBF`

**Purpose:** Primary work order and service ticket database - the heart of daily operations

#### Data Structure

**Customer Information:**
- `FIRSTNAME`, `LASTNAME` - Customer name
- `ADDRESS` - Street address
- `CITY`, `STATE`, `ZIP` - Location
- `PHONE` - Contact number
- `PHTYPE` - Phone type (home, work, mobile)

**Device/Appliance Information:**
- `MAKE` - Manufacturer (Whirlpool, Samsung, LG, GE, Frigidaire, etc.)
- `TYPE` - Device type abbreviations:
  - `dw` = dishwasher
  - `ref` = refrigerator
  - `washer` = washing machine
  - `dryer` = clothes dryer
  - `range` = stove/oven
  - `mw` = microwave
- `MODEL` - Model number
- `SERIAL` - Serial number
- `DATEPURCHASED` / `DATEPUR` - Purchase date

**Service Request Information:**
- `SERVICEREQ` - Customer's reported problem ("won't start", "leaking water", "not cooling", etc.)
- `WORKDONE` - Technician's description of service performed ("replaced pump", "adjusted belt", "cleared drain line")
- `NOTES` - Additional notes and memos
- `STATUS` - Current ticket status
- `LOCATION` - Storage/work location code
- `TICLOC` - Ticket location identifier

**Date Tracking:**
- `DATEIN` - When device was received/checked in
- `DATEPROM` - Promised completion date (typically DATEIN + 7 days)
- `DATECOMPLT` - Actual completion date (validated: must be between DATEIN and today)
- `DATEOUT` - When customer picked up device

**Parts Used (11 slots available):**
- `P1` through `P11` - Part names/identifiers
- `PD1` through `PD11` - Part descriptions
- `Q1` through `Q11` - Quantities used
- `C1` through `C11` - Cost per part

**Financial Fields:**
- `PARTS` - Total parts cost (calculated)
- `REG_LABOR` - Regular labor charge
- `WARR_LABOR` - Warranty labor (typically $0 customer charge)
- `TRIP` - Trip/travel charge
- `SHOPSUPPLY` - Shop supplies charge
- `OTHER` - Miscellaneous charges
- `DEPOSIT` - Deposit or partial payment
- `INVOICE` - Invoice number (your company)
- `DLRINVOICE` - Dealer invoice reference
- `HOWPAID` - Payment method (cash, check, credit card, account, etc.)
- `Grand Total` - Calculated total of all charges

#### Main Views (User Interfaces)

**Switchboard** (Main Menu/Dashboard)
- Entry point when opening database
- Date range selector with visual pay period navigation
- Buttons:
  - **PrevBut** - Navigate to previous pay period
  - **NextBut** - Navigate to next pay period
  - **SJ Find** - Sales Journal search button
- Displays current date range (1st-14th or 15th-end of month)

**WorkOrder View**
- Default view when opening database
- Initial ticket entry form
- Quick data entry layout

**Service Call Form**
- Detailed service information entry
- Comprehensive field display
- Primary working view for technicians

**Parts Form**
- Focused view for parts entry and tracking
- Shows P1-P11, Q1-Q11, C1-C11 fields prominently
- Parts lookup integration

**Final Copy**
- Print-ready invoice layout
- Customer-facing format
- Contains all charges and totals
- Professional formatting for customer delivery

**Customer Copy**
- Customer-facing print format
- May have different field visibility than Final Copy

**Ticket View**
- Ticket-style compact layout
- Quick reference format

**SalesJournal View** (Financial Reporting)
- Revenue reporting by date range
- **Query logic:** `CustData.Grand Total > 0 AND Payments.Finalize BETWEEN [start date] AND [end date]`
- Used for end-of-period financial reconciliation
- Links to Payments.APR for finalized payment dates

**Income Report, No Money Copy, and various other report views**

#### Database Relationships
**Links to:**
- `Payments.APR` - Via INVOICE field for payment tracking
- `memo.APR` - For ticket notes and memos with timestamps
- `LOCATION TAGS.APR` - Via TICLOC field for location organization

**Triggers:**
- When parts (P1-P11) are entered, records are created in `Partlog.APR`

---

### 2. Partlog.APR (Parts Inventory Tracking)
**Underlying file:** `Partlog.DBF`

**Purpose:** Track every part from order → receipt → stock → installation → potential return

#### Data Structure

**Part Identification:**
- `PART_NUM` - Part number (indexed)
- `PART_DESCR` - Part description (indexed)
- `VENDOR` - Supplier name (indexed, typically "Marcone")

**Financial Information:**
- `COST` - Cost of part
- `INVOICE` - Your internal invoice number (indexed)
- `MAN_INVOIC` - Manufacturer/supplier invoice number (indexed)
- `PONUMBER` - Purchase order number (indexed)

**Location and Storage:**
- `LOCATION` - Storage location identifier (indexed)
- Multiple indexed for fast location-based queries

**Tracking Information:**
- `TRACKING` - Shipment tracking number (indexed)
- `RA_NUMBER` - Return authorization number (indexed)
- `ORDCONF` - Order confirmation (indexed)
- `DUD` - Defective/dud part flag (indexed)
- `DATEORD` - Date ordered (indexed)
- `DATE_OF_RE` - Date of receipt (indexed)
- `LOCUPDATE` - Location update timestamp

**Timestamps:**
- `CREDATE` - Creation date (indexed)
- `CRETIME` - Creation time
- Used together for chronological sorting and audit trail

**Special Linking Fields:**

**TIMEKEY** (Unique Identifier)
- **Type:** Numeric, 14 digits
- **Formula:**
  ```
  Right(Year(Today()), 1) * 100000000000 +
  DayOfYear(Today()) * 100000000 +
  Hour(CurrTime()) * 1000000 +
  Minute(CurrTime()) * 10000 +
  Second(CurrTime()) * 100 +
  (Random() * 99)
  ```
- **Components:**
  - Last digit of year (e.g., 5 for 2025) × 100000000000
  - Day of year (1-366) × 100000000
  - Hour (0-23) × 1000000
  - Minute (0-59) × 10000
  - Second (0-59) × 100
  - Random 2-digit number (0-99)
- **Example:** `50201234512345` = Year 2025, day 20, 12:34:51.23 + random
- **Purpose:** Collision-resistant unique identifier for each part transaction

**KEY** (Composite Linking Field)
- **Formula (modified 7/10/25):**
  ```
  Combine(Trim(Partlog.COST), '  ', Trim(Partlog.MAN_INVOIC), '  ', Trim(Partlog.PART_NUM))
  ```
- **Components:** COST + double-space + INVOICE + double-space + PART_NUM
- **Purpose:** Links Partlog records to MARCONE AVAILABLE RETURNS.APR
- **Use case:** Identifies which parts are eligible for return credit
- **Indexed:** Yes (for fast lookups)

**COMBO** (Combination field, indexed)

**ResolvedPn** (Resolved Part Number)
- Links variant part numbers to standard/superseded part numbers
- Allows finding all versions of a part across databases
- Used when a part has been superseded or has multiple manufacturer numbers

**PRINT** (Print flag, indexed)
- Controls whether part appears on reports

#### Database Relationships
**Updates triggered to:**
- `STOCK ONLY.APR` - Inventory reduction when part is used
- `DISTINCTLOCATIONS.APR` - Location-specific stock level updates

**Links to:**
- `MARCONE AVAILABLE RETURNS.APR` - Via KEY field for return eligibility
- `MARCONE SALES AND CREDITS.APR` - Via KEY field for transaction reconciliation
- `PNPDC.APR` - Part number to price/cost conversion
- `VENDOR2.APR` - Vendor information and performance
- `9999.APR` - Via ResolvedPn for problem parts requiring resolution

---

### 3. Marcone Supplier Databases (Parts Supplier Integration)

Marcone is a major appliance parts distributor. Multiple APR files manage the complete supplier relationship:

#### MARCONE ORDERS.APR
- **Purpose:** Track orders placed to Marcone
- **Contains:** Order dates, part numbers, quantities, expected delivery
- **Use case:** Monitor outstanding orders

#### MARCONE AVAILABLE RETURNS.APR
- **Purpose:** Parts eligible for return credit
- **Key field:** KEY (matches Partlog.KEY)
- **Use case:** Identify which parts in stock can be returned for credit
- **Business value:** Recover costs on excess or wrong parts

#### MARCONE SALES AND CREDITS.APR
- **Purpose:** Transaction history with Marcone
- **Contains:** Sales charges, credit memos, adjustments
- **Key field:** KEY (matches Partlog.KEY)
- **Use case:** Financial reconciliation

#### DupMarcCredits.APR
- **Purpose:** MARCONE SALES AND CREDITS with duplicate handling
- **Use case:** Resolving duplicate transactions

#### Marcone tracking.APR
- **Purpose:** Shipment and delivery tracking
- **Contains:** Tracking numbers, delivery dates, carrier info
- **Use case:** Monitor deliveries and resolve shipping issues

#### MARCONE UPDATE.APR
- **Purpose:** Real-time updates from supplier
- **Use case:** Sync latest pricing, availability, and account status

**How Marcone Integration Works:**
1. Part used in service call → Partlog record created with KEY field
2. KEY field = COST + INVOICE + PART_NUM combined
3. KEY is looked up in MARCONE AVAILABLE RETURNS
4. If match found → part is eligible for return credit
5. Credits processed through MARCONE SALES AND CREDITS
6. Financial reconciliation at end of period

---

### 4. Stock Management Databases

#### STOCK ONLY.APR
- **Purpose:** Current inventory on hand
- **Updated by:** Parts usage from service tickets (reduces stock)
- **Contains:** Part numbers, quantities available, locations
- **Real-time:** Updated as parts are used in STATUSUPDATE

#### DISTINCTLOCATIONS.APR
- **Purpose:** Stock levels by storage location
- **Organization:** 10% increment buckets (0-10%, 10-20%, etc.)
- **Contains:** Location identifiers, stock status indicators
- **Use case:** Quick visual reference of inventory distribution
- **Master list:** All storage locations in system

#### STOCK RATIO.APR
- **Purpose:** Stock-to-demand ratio analysis
- **Calculation:** Inventory on hand vs. historical usage
- **Use case:** Identify overstocked and understocked parts
- **Business value:** Optimize inventory investment

#### 9999.APR
- **Purpose:** Catch-all database for parts requiring resolution
- **Contains:** Parts with issues (wrong part number, superseded, unidentifiable)
- **ResolvedPn field:** Links problem parts to correct part numbers
- **Use case:** Clean up inventory data and resolve part number conflicts

#### CORES.APR
- **Purpose:** Core parts (exchangeable components) management
- **Contains:** Compressors, motors, and other core-exchange parts
- **Business model:** Return old part for credit when installing new one
- **Use case:** Track core inventory and credit eligibility

#### Loaner.APR
- **Purpose:** Loaner units tracking
- **Contains:** Temporary replacement appliances
- **Use case:** Track which customers have loaner units and when they're due back

#### Subs.APR
- **Purpose:** Substitute parts cross-reference
- **Contains:** Part number substitutions and equivalents
- **Use case:** When primary part unavailable, find acceptable substitute
- **Example:** Part A123 can be substituted with Part A124 or B789

---

### 5. Reference and Lookup Databases

#### LOC.APR / LOC.dbf
- **Purpose:** Location reference codes
- **Contains:** Location abbreviations and full names
- **Use case:** Standardize location data entry

#### LOCATION TAGS.APR
- **Purpose:** Organizational tags for storage locations
- **Contains:** Tag categories, descriptions, hierarchies
- **Use case:** Group locations by region, type, or business unit

#### LOCATION TAG EXPERIMENT.APR
- **Purpose:** New location tagging system (experimental/testing)
- **Status:** Development/testing phase
- **Use case:** Evaluate improved location organization before production rollout

#### SHRTMAKE.APR
- **Purpose:** Shortened manufacturer names and codes
- **Examples:**
  - Samsung → SS
  - Whirlpool → WP
  - LG → LG
  - GE → GE
  - Frigidaire → FRI
- **Use case:** Standardize manufacturer entry, save space in reports

#### STREET NAMES.APR / LINCOLN STREET NAMES.APR
- **Purpose:** Address standardization
- **Contains:** Standard street name abbreviations
- **Use case:** Ensure consistent address formatting
- **Geographic scope:** General street names + Lincoln, NE specific

#### DISTANCE.APR
- **Purpose:** Geographic distance calculations
- **Contains:** Distances between service locations
- **Use case:** Route optimization, trip charge calculation, technician assignment

#### PNPDC.APR
- **Purpose:** Part Number to Price and Description Conversion
- **Contains:** Part numbers with standard pricing and descriptions
- **Use case:** Quick lookup for pricing, standardize descriptions

#### baseissues.APR
- **Purpose:** Standard problem codes and descriptions
- **Contains:** Common issue descriptions (not cooling, won't drain, noise, etc.)
- **Use case:** Standardize SERVICEREQ field entries for reporting

---

### 6. Reporting and Analysis Databases

#### CHARTS.APR
- **Purpose:** Dashboard charts and analytics
- **Visualizations:** Revenue trends, parts usage, technician productivity
- **Use case:** Management oversight and business intelligence

#### Part and quantity.APR
- **Purpose:** Parts inventory count analysis
- **Contains:** Part-level quantity summaries
- **Use case:** Inventory valuation and turnover analysis

#### PART EXPORT.APR
- **Purpose:** Parts data export format
- **Contains:** Formatted part data for external systems
- **Use case:** Export to accounting, ordering, or reporting systems

#### PARTBYINVOICE.APR
- **Purpose:** Parts organized by invoice
- **Contains:** Invoice-level part summaries
- **Use case:** Invoice reconciliation and analysis

#### SDRATIO.APR
- **Purpose:** Stock distribution ratios
- **Calculation:** How inventory is distributed across locations
- **Use case:** Balance inventory across service locations

#### Table DATA.APR
- **Purpose:** Linked data views across multiple databases
- **Contains:** Joined/merged data from multiple sources
- **Use case:** Complex reporting requiring data from multiple APR files

#### VENDOR2.APR
- **Purpose:** Vendor performance analysis
- **Contains:** Vendor metrics (delivery time, pricing, quality)
- **Use case:** Vendor evaluation and negotiation

#### MicroMnSn.APR
- **Purpose:** Micro-analytics on Make/Model/Serial data
- **Contains:** Device failure patterns, common issues by model
- **Use case:** Identify problematic models, predict part needs

#### Table data.txt
- **Purpose:** Raw customer call data export (sample/reference)
- **Format:** Text file with field-delimited data
- **Use case:** Documentation and external processing

---

### 7. Payment Processing

#### Payments.APR
- **Purpose:** Payment records with finalization tracking
- **Key field:** `Finalize` - Date/time payment was finalized
- **Links from:** STATUSUPDATE.APR via INVOICE field
- **Use case:** Financial reporting and cash flow tracking
- **Critical for:** SalesJournal queries (only finalized payments count as revenue)

---

### 8. Specialized Purpose Databases

#### memo.APR
- **Purpose:** Memo and notes field with timestamp tracking
- **Fields:**
  - Memo text
  - Created date/time
  - Modified date/time
- **Use case:** Track notes on tickets, detect dormant tickets (no recent modifications)
- **Links from:** STATUSUPDATE.APR

#### FINDTRACKING.APR
- **Purpose:** Search and tracking utility
- **Use case:** Complex searches across multiple databases

#### DMI.dbf
- **Purpose:** Possible data management interface (undocumented)

#### holder.APR / keeper.APR
- **Purpose:** Data holding/temporary storage databases
- **Use case:** Temporary data during batch operations or migrations

---

## Daily User Workflow

### Morning - Dispatch and Scheduling

**Step 1: Open System**
- Navigate to `Y:\Lotus\`
- Open `STATUSUPDATE.APR`
- System opens to **Switchboard** view (main menu)

**Step 2: View Schedule**
- Switchboard displays current pay period date range
- System auto-calculates range based on today's date:
  - If today is 1st-14th → displays 1st-14th range
  - If today is 15th-end → displays 15th-end of month range
- Review tickets with promised dates (`DATEPROM`) for today

**Step 3: Navigate Date Ranges**
- Click **PrevBut** to view previous pay period
  - If currently viewing 1st-14th → jumps to 15th-end of previous month
  - If currently viewing 15th-end → jumps to 1st-14th of same month
- Click **NextBut** to view next pay period
  - If currently viewing 1st-14th → jumps to 15th-end of same month
  - If currently viewing 15th-end → jumps to 1st-14th of next month

**Step 4: Assign Work**
- Review open tickets by location (`TICLOC`)
- Check promised dates to prioritize
- Assign technicians based on location and workload

---

### Service Call - Recording Work

#### Creating New Ticket

**Option A: Duplicate Existing Ticket (Common for returning customers)**
1. Find existing ticket for customer
2. Click **dup** button or run `dup` script
3. System creates copy with:
   - **Kept:** Customer info (name, address, phone)
   - **Cleared:** Device info, parts, labor, payment, dates (except DATEIN/DATEPROM)
   - **Set automatically:**
     - `DATEIN` = Today
     - `DATEPROM` = Today + 7 days
     - All quantities (`Q1-Q11`) = empty string ('')
     - All part fields cleared (`P1-P11`, `PD1-PD11`, `C1-C11`)
     - Labor fields cleared (`REG_LABOR`, `WARR_LABOR`, `TRIP`)
     - Service fields cleared (`MAKE`, `TYPE`, `MODEL`, `SERIAL`, `SERVICEREQ`, `WORKDONE`, `NOTES`)
     - Payment cleared (`HOWPAID`)
4. Works in both **Form** and **Worksheet** views (detected via `$AprWorkSheet` check)

**Option B: Create New Ticket**
1. In WorkOrder view, create new record
2. System prompts for customer information
3. All fields start empty

#### Data Entry Process

**1. Customer Information**
- `FIRSTNAME` - First name
- `LASTNAME` - Last name
- `ADDRESS` - Street address
- `CITY` - City name
- `STATE` - State abbreviation (NE, IA)
- `ZIP` - Zip code
- `PHONE` - Phone number
- `PHTYPE` - Phone type (Home, Work, Mobile, Cell)

**Focus scripts available:**
- `FocFName` - Jump to First Name
- `FocPh1` - Jump to Phone

**2. Device/Appliance Information**
- `MAKE` - Manufacturer name (Whirlpool, Samsung, LG, etc.)
  - Focus script: `FocMake`
  - Can use `SHRTMAKE.APR` for abbreviated codes
- `TYPE` - Device type:
  - `dw` - Dishwasher
  - `ref` - Refrigerator
  - `washer` - Washing machine
  - `dryer` - Clothes dryer
  - `range` - Stove/oven/range
  - `mw` - Microwave
  - Focus script: `FocTyp`
- `MODEL` - Model number
  - Focus script: `FocModel`
- `SERIAL` - Serial number
  - Focus script: `FocSerial`
- `DATEPURCHASED` - Purchase date
  - Focus script: `FocDatePur`

**3. Service Request**
- `SERVICEREQ` - Customer's reported problem
  - Focus script: `FocSympt`
  - Examples: "Won't start", "Leaking water", "Not cooling", "Making noise", "Won't drain"
  - Can reference `baseissues.APR` for standard problem codes

**4. Location Assignment**
- `TICLOC` - Ticket location code
  - Focus script: `FocTicLoc`
  - References `LOCATION TAGS.APR`
- `LOCATION` - Storage/work location
  - References `LOC.APR` and `DISTINCTLOCATIONS.APR`

**5. Dates**
- `DATEIN` - Automatically set when ticket created (Today)
- `DATEPROM` - Automatically set (DATEIN + 7 days)
- Can be manually adjusted if needed

#### During/After Service Work

**6. Work Performed**
- `WORKDONE` - Description of service performed
  - Examples: "Replaced evaporator fan motor", "Cleared drain hose", "Adjusted door latch", "Replaced control board"
  - Be specific for future reference and warranty tracking

**7. Notes**
- `NOTES` - Additional information
  - Special instructions
  - Follow-up needed
  - Warranty information
  - Customer requests
- Linked to `memo.APR` for timestamp tracking

**8. Parts Used**
- **For each part used (up to 11 parts per ticket):**

  **Part 1 (repeat for P2-P11, Q2-Q11, C2-C11):**
  - `P1` - Part name/identifier
  - `PD1` - Part description
  - `Q1` - Quantity used
    - Focus script: `FocQ1` through `FocQ10`
    - MUST be numeric or empty string ('')
    - Set by `dup` script to '' (empty string, not 0)
  - `C1` - Cost per part

  **Example:**
  - P1 = "WP12345678"
  - PD1 = "Evaporator fan motor"
  - Q1 = "1"
  - C1 = "$45.00"

**Behind the scenes when parts entered:**
- System creates record in `Partlog.APR`
- `TIMEKEY` generated (unique 14-digit identifier)
- `KEY` field calculated: `Combine(COST, MAN_INVOIC, PART_NUM)`
- `STOCK ONLY.APR` updated (inventory reduced)
- `DISTINCTLOCATIONS.APR` updated (location stock levels)
- If Marcone part, `MARCONE AVAILABLE RETURNS.APR` checked for return eligibility

**9. Labor Charges**
- `REG_LABOR` - Regular labor charge
  - Billable customer labor
- `WARR_LABOR` - Warranty labor
  - Tracked separately (typically $0 to customer, reimbursed by manufacturer)
- `TRIP` - Trip/travel charge
  - Distance-based, may reference `DISTANCE.APR`

**10. Other Charges**
- `SHOPSUPPLY` - Shop supplies
- `OTHER` - Miscellaneous charges
- `DEPOSIT` - Deposit or partial payment received

**11. Completion**
- `DATECOMPLT` - Completion date
  - Focus script: `FocDateout`
  - **Validation formula:**
    ```
    CUSTDATA.DATECOMPLT = '' OR
    (CUSTDATA.DATECOMPLT <= Today() AND CUSTDATA.DATECOMPLT >= CUSTDATA.DATEIN)
    ```
  - Ensures:
    - Either empty (not complete)
    - OR between DATEIN and today (logical date range)
  - **Known issue:** Validation can cause errors during ticket duplication

**12. Invoice Generation**
- `INVOICE` - Your company invoice number
  - Focus script: `FocInvoice`
- `DLRINVOICE` - Dealer invoice (if applicable)
  - Focus script: `FocDlrInv`
- Switch to **Final Copy** view
- Print customer invoice

**13. Payment**
- `HOWPAID` - Payment method
  - Cash
  - Check
  - Credit card (Visa, MC, Amex, Discover)
  - Account/Charge
  - Warranty
  - Other
- Record amount received
- System calculates `Grand Total` automatically (PARTS + REG_LABOR + WARR_LABOR + TRIP + SHOPSUPPLY + OTHER - DEPOSIT)

**14. Payment Finalization**
- Payment recorded in `Payments.APR`
- `Finalize` field set to current date/time
- This timestamp critical for SalesJournal reporting

**15. Checkout**
- `DATEOUT` - Date customer picked up device
- Close ticket
- File paperwork

---

### Parts Tracking - Behind the Scenes

When parts are entered in STATUSUPDATE (P1-P11 fields), the following automated processes occur:

**1. Partlog Record Creation**
- New record created in `Partlog.APR`
- Fields populated:
  - `PART_NUM` = from P1-P11
  - `PART_DESCR` = from PD1-PD11
  - `COST` = from C1-C11
  - `INVOICE` = from STATUSUPDATE.INVOICE
  - `VENDOR` = (if known, typically "Marcone")
  - `LOCATION` = from STATUSUPDATE.TICLOC or LOCATION
  - `CREDATE` = Today
  - `CRETIME` = Current time

**2. Unique Identifier Generation**
- `TIMEKEY` calculated using formula:
  ```
  Right(Year(Today()), 1) * 100000000000 +
  DayOfYear(Today()) * 100000000 +
  Hour(CurrTime()) * 1000000 +
  Minute(CurrTime()) * 10000 +
  Second(CurrTime()) * 100 +
  (Random() * 99)
  ```
- Example result: `50201234512345`
- Ensures uniqueness even with multiple simultaneous entries

**3. Marcone Linking**
- `KEY` field calculated:
  ```
  Combine(Trim(Partlog.COST), '  ', Trim(Partlog.MAN_INVOIC), '  ', Trim(Partlog.PART_NUM))
  ```
- This KEY links to:
  - `MARCONE AVAILABLE RETURNS.APR` - Check if part eligible for return
  - `MARCONE SALES AND CREDITS.APR` - Transaction reconciliation

**4. Stock Updates**
- `STOCK ONLY.APR` accessed
- Part quantity reduced by Q1-Q11 value
- If stock drops below threshold, alert may trigger

**5. Location Stock Tracking**
- `DISTINCTLOCATIONS.APR` updated
- Location-specific stock level modified
- 10% bucket status may change

**6. Return Eligibility Check**
- System queries `MARCONE AVAILABLE RETURNS.APR`
- Matches on KEY field
- If match found, part marked as returnable
- Return eligibility noted for end-of-period processing

---

### End of Pay Period - Financial Reporting

**Pay Period Structure:**
- **Period 1:** 1st through 14th of month
- **Period 2:** 15th through end of month (28th, 29th, 30th, or 31st)

**Step 1: Navigate to Period**
1. Open `STATUSUPDATE.APR` to Switchboard
2. Use **PrevBut** / **NextBut** to select desired period
3. System displays date range in view

**Step 2: Run Sales Journal**
1. Click **SJ Find** button
2. System executes query:
   ```
   CustData.Grand Total > 0
   AND
   Payments.Finalize BETWEEN [start date] AND [end date]
   ```
3. **SalesJournal** view opens with filtered results
4. Shows all completed, paid, and finalized tickets

**Step 3: Review Results**
- Verify all expected invoices present
- Check totals match expectations
- Review payment methods distribution

**Step 4: Print Report**
- Click **PrintPre** (Print Preview) button
- Review layout
- Print for accounting/records
- File in appropriate period folder

**Step 5: Marcone Reconciliation**
1. Open `MARCONE SALES AND CREDITS.APR`
2. Filter by date range
3. Match Partlog KEY fields to Marcone transactions
4. Identify parts eligible for return credit
5. Process returns through `MARCONE AVAILABLE RETURNS.APR`
6. Submit return authorizations (RA_NUMBER)

**Step 6: Stock Analysis**
1. Open `STOCK RATIO.APR`
2. Review inventory levels vs. demand
3. Identify overstocked parts (return candidates)
4. Identify understocked parts (order candidates)
5. Open `DISTINCTLOCATIONS.APR` to see location distribution

**Step 7: Financial Close**
- Export data if needed via `PART EXPORT.APR`
- Archive period data
- Prepare for next period

---

## LotusScript Automation and Macros

### LotusScript Overview
**Language:** LotusScript (Lotus Domino era technology, circa 2000)
**Paradigm:** Object-oriented with event-driven programming
**Key objects:** Form, View, Application, Document, Window, Query, Connection

### Global Utility Scripts

#### `Bp` - Beep Alert
**Purpose:** Audio feedback for user actions
**Usage:** Called when action completes or error occurs
**Code:** `Beep` command

#### `ClearSaveFlag` - Mark Unmodified
**Purpose:** Mark current document as unmodified (remove dirty flag)
**Usage:** After saving or when canceling changes
**Code:** Document dirty flag = False

#### `connecttodb` - Database Connection
**Purpose:** SQL connection to external dBase IV databases
**Technology:** ODBC connection
**Usage:** When querying external data sources or legacy systems
**Returns:** Connection object

#### `Refresh` - Refresh Window
**Purpose:** Refresh current view/window
**Usage:** After data changes to update display
**Code:** `ActiveWindow.Refresh` or `IDM_REFRESH`

#### `sleep1` - Pause Execution
**Purpose:** 10-second pause
**WARNING:** Locks up interface during pause (blocking operation)
**Usage:** Timing-sensitive operations (rare use)
**Code:** Sleep/wait command for 10000 milliseconds

#### `SubRed` - Visual Feedback
**Purpose:** Flash background red then white
**Usage:** Visual alert for errors or important actions
**Implementation:**
  1. Set form background to red
  2. Pause briefly
  3. Set form background to white
  4. Refresh display

### Ticket Management Scripts

#### `dup` - Duplicate Ticket (MOST IMPORTANT)
**Purpose:** Create copy of current ticket for same customer with different device

**Behavior:**
1. **Checks view type:** Form view vs. Worksheet view (via `$AprWorkSheet` property)
2. **Creates duplicate record**
3. **Clears these fields:**
   - Device: `MAKE`, `TYPE`, `MODEL`, `SERIAL`
   - Service: `SERVICEREQ`, `WORKDONE`, `NOTES`, `STATUS`
   - Dates: `DATECOMPLT`, `DATEOUT`
   - Parts: `P1-P11`, `PD1-PD11`, `C1-C11`, `Q1-Q11`
   - Labor: `REG_LABOR`, `WARR_LABOR`, `TRIP`
   - Location: `LOCATION`, `TICLOC`
   - Payment: `HOWPAID`
4. **Sets these fields:**
   - `DATEIN` = Today()
   - `DATEPROM` = Today() + 7 days
   - `Q1` through `Q11` = '' (empty string, not zero!)
5. **Keeps these fields:**
   - Customer: `FIRSTNAME`, `LASTNAME`, `ADDRESS`, `CITY`, `STATE`, `ZIP`, `PHONE`, `PHTYPE`
   - Invoice: `INVOICE` (may increment)

**Critical notes:**
- Quantities set to '' (empty string) not 0 (zero) - distinction matters for calculations
- Works in both Form and Worksheet contexts
- Most commonly used script in daily operations
- **Known issue:** Can trigger DATECOMPLT validation errors (ticket filed in version notes)

### Focus Navigation Scripts

**Purpose:** Move cursor to specific field for faster data entry

**Available focus scripts:**
- `FocAskSlot` - Ask/slot field
- `FocDateout` - Date out field
- `FocDatePur` - Date purchased field
- `FocDealercity` - Dealer city
- `FocDlrInv` - Dealer invoice
- `FocDlrname` - Dealer name
- `FocFName` - First name
- `FocInvoice` - Invoice number
- `FocMake` - Make/manufacturer
- `FocModel` - Model number
- `FocPh1` - Phone number
- `FocQ1` through `FocQ10` - Quantity fields 1-10
- `FocSerial` - Serial number
- `FocSympt` - Symptom/service request
- `FocTicLoc` - Ticket location
- `FocTyp` - Type field

**Implementation:** Each uses `.SetFocus` method on the target field

**Usage pattern:**
```lotusscript
Sub FocMake(s As String)
    CUSTDATA.MAKE.SetFocus
End Sub
```

**Keyboard shortcuts:** Likely bound to function keys or keyboard combinations for quick navigation during data entry

### Date Handling Scripts

#### `SetDates` - Auto-Calculate Pay Period
**Purpose:** Automatically set date range based on current day of month

**Logic:**
```
If Day(Today()) >= 15 Then
    VarStDate = Date(Year(Today()), Month(Today()), 15)
    VarEndDate = EndOfMonth(Today())
Else
    VarStDate = Date(Year(Today()), Month(Today()), 1)
    VarEndDate = Date(Year(Today()), Month(Today()), 14)
End If
```

**Display:** Updates form with `Cstr()` conversion for text display

**Triggers:**
- On form open
- On Switchboard navigation
- When PrevBut/NextBut clicked

### Window and View Control Scripts

#### `ltrt` - Tile Windows
**Purpose:** Tile windows left/right
**Code:** `IDM_TILE_LEFT_RIGHT` menu command
**Usage:** When working with multiple views simultaneously

#### `PrintPre` - Print Preview
**Purpose:** Show print preview of current view
**Code:** `IDM_PRINT_PREVIEW` menu command
**Usage:** Before printing invoices or reports

#### `PrintWO` - Print Work Orders
**Purpose:** Print work orders with sorting
**Implementation:**
  1. Prompt for sort order
  2. Apply sort
  3. Generate print job
  4. Queue to default printer

#### `SJFind` - Sales Journal Finder
**Purpose:** Find and display Sales Journal records for date range
**Query:**
```
CustData.Grand Total > 0
AND
Payments.Finalize BETWEEN VarStDate AND VarEndDate
```
**Steps:**
  1. Get date range from Switchboard (VarStDate, VarEndDate)
  2. Execute query against CUSTDATA joined with Payments
  3. Open SalesJournal view with results
  4. Optionally trigger PrintPreview

#### `OpnPymt` - Open Payments Database
**Purpose:** Dynamically open Payments.apr database
**Implementation:**
```lotusscript
Sub OpnPymt(s As String)
    Dim app As New Application
    app.OpenDatabase("Y:\Lotus\Payments.apr")
End Sub
```
**Usage:** When needing to view/edit payment records directly

### Button Click Handlers (Switchboard)

#### `PrevBut` - Previous Period Button
**Purpose:** Navigate to previous pay period

**Logic:**
```
If Day(VarStDate) = 1 Then
    ' Currently viewing 1st-14th, go to 15th-end of PREVIOUS month
    VarStDate = Date(Year(VarStDate), Month(VarStDate) - 1, 15)
    VarEndDate = EndOfMonth(Date(Year(VarStDate), Month(VarStDate) - 1, 1))
Else
    ' Currently viewing 15th-end, go to 1st-14th of SAME month
    VarStDate = Date(Year(VarStDate), Month(VarStDate), 1)
    VarEndDate = Date(Year(VarStDate), Month(VarStDate), 14)
End If
```

**Updates:** Refreshes view with new date range

**Examples:**
- Viewing Jan 1-14 → Click PrevBut → Shows Dec 15-31
- Viewing Jan 15-31 → Click PrevBut → Shows Jan 1-14

#### `NextBut` - Next Period Button
**Purpose:** Navigate to next pay period

**Logic:**
```
If Day(VarStDate) = 1 Then
    ' Currently viewing 1st-14th, go to 15th-end of SAME month
    VarStDate = Date(Year(VarStDate), Month(VarStDate), 15)
    VarEndDate = EndOfMonth(VarStDate)
Else
    ' Currently viewing 15th-end, go to 1st-14th of NEXT month
    VarStDate = Date(Year(VarStDate), Month(VarStDate) + 1, 1)
    VarEndDate = Date(Year(VarStDate), Month(VarStDate) + 1, 14)
End If
```

**Updates:** Refreshes view with new date range

**Examples:**
- Viewing Jan 1-14 → Click NextBut → Shows Jan 15-31
- Viewing Jan 15-31 → Click NextBut → Shows Feb 1-14

#### `SJ Find Button` - Execute Sales Journal Search
**Purpose:** Run sales journal query and display results

**Steps:**
1. Get current date range (VarStDate, VarEndDate)
2. Execute SJFind script
3. Display SalesJournal view
4. Trigger PrintPreview automatically

**Query executed:** (as described in SJFind above)

### Data Export Scripts

#### `Sub2` - Export Data
**Purpose:** Export database records to external format
**Format:** Likely CSV or text-delimited
**Destination:** File system or external database
**Usage:** End-of-period data backup or accounting system integration

### Data Validation Formulas

#### DATECOMPLT Validation
**Field:** `CUSTDATA.DATECOMPLT`

**Formula:**
```
CUSTDATA.DATECOMPLT = ''
OR
(CUSTDATA.DATECOMPLT <= Today() AND CUSTDATA.DATECOMPLT >= CUSTDATA.DATEIN)
```

**Purpose:** Ensure completion date is logical

**Rules:**
1. **Option 1:** Field is empty (work not completed yet) - Valid
2. **Option 2:** Both conditions must be true:
   - Completion date is not in the future (≤ Today)
   - Completion date is not before check-in (≥ DATEIN)

**Error message:** Triggered when user enters invalid date

**Known issue:** Can cause problems during ticket duplication (documented in version notes)

**Workaround:** May need to temporarily clear DATECOMPLT during dup operation

---

## Database Relationships and Data Flow

### Primary Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│          Customer brings in broken appliance            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Create ticket in STATUSUPDATE.APR (CUSTDATA.DBF)      │
│  - Customer info (name, address, phone)                 │
│  - Device info (make, model, serial, type)              │
│  - Problem description (SERVICEREQ)                     │
│  - Date in, Date promised                               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│         Technician diagnoses and repairs device         │
│         Records WORKDONE field                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Enter parts used (P1-P11, Q1-Q11, C1-C11)             │
└─────────────────────┬───────────────────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
┌──────────────────────┐  ┌──────────────────────┐
│  Partlog.APR record  │  │  STOCK ONLY.APR      │
│  created with:       │  │  Inventory reduced   │
│  - TIMEKEY (unique)  │  │  by Q1-Q11           │
│  - KEY (Marcone link)│  └──────────┬───────────┘
│  - CREDATE/TIME      │             │
└──────────┬───────────┘             │
           │                         │
           │                         ▼
           │             ┌──────────────────────┐
           │             │ DISTINCTLOCATIONS.APR│
           │             │ Location stock       │
           │             │ levels updated       │
           │             └──────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│  KEY field links to Marcone databases:                  │
│  - MARCONE AVAILABLE RETURNS.APR                        │
│    (Check if part eligible for return credit)          │
│  - MARCONE SALES AND CREDITS.APR                        │
│    (Transaction reconciliation)                         │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Complete ticket:                                       │
│  - Set DATECOMPLT (completion date)                     │
│  - Switch to Final Copy view                            │
│  - Print invoice                                        │
│  - Record payment method (HOWPAID)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Payment recorded in Payments.APR                       │
│  - Invoice number                                       │
│  - Amount                                               │
│  - Finalize timestamp (critical for reporting!)         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  End of pay period:                                     │
│  - Click "SJ Find" button in Switchboard                │
│  - SalesJournal query executes:                         │
│    Grand Total > 0 AND Finalize in date range           │
│  - Generate financial report                            │
│  - Marcone reconciliation for returns                   │
└─────────────────────────────────────────────────────────┘
```

### Key Linking Mechanisms

#### 1. INVOICE Field (Primary Key)
**Links:** STATUSUPDATE.APR ↔ Payments.APR

**Flow:**
- Invoice number generated in STATUSUPDATE
- Payment record created in Payments.APR with same invoice number
- Join on INVOICE for SalesJournal reporting

#### 2. TIMEKEY (Unique Part Transaction ID)
**Location:** Partlog.APR

**Formula:**
```
Right(Year(Today()), 1) * 100000000000 +
DayOfYear(Today()) * 100000000 +
Hour(CurrTime()) * 1000000 +
Minute(CurrTime()) * 10000 +
Second(CurrTime()) * 100 +
(Random() * 99)
```

**Components:**
- Position 1: Last digit of year (5 for 2025)
- Positions 2-4: Day of year (001-366)
- Positions 5-6: Hour (00-23)
- Positions 7-8: Minute (00-59)
- Positions 9-10: Second (00-59)
- Positions 11-14: Random number (00-99) for collision prevention

**Example:** `50201234512345`
- Year: 2025 (5)
- Day: 020 (20th day of year = January 20)
- Time: 12:34:51
- Random: 23
- Full: 5 + 020 + 12 + 34 + 51 + 23 = 50201234512345 (14 digits)

**Purpose:** Unique identifier for each part transaction, even when multiple parts entered simultaneously

#### 3. KEY Field (Marcone Linking)
**Formula (modified 7/10/25):**
```
Combine(Trim(Partlog.COST), '  ', Trim(Partlog.MAN_INVOIC), '  ', Trim(Partlog.PART_NUM))
```

**Links:** Partlog.APR ↔ MARCONE AVAILABLE RETURNS.APR ↔ MARCONE SALES AND CREDITS.APR

**Example:**
- COST = "45.00"
- MAN_INVOIC = "INV123456"
- PART_NUM = "WP12345678"
- KEY = "45.00  INV123456  WP12345678"

**Purpose:**
- Match parts in inventory to Marcone's return eligibility list
- Reconcile credits and charges with supplier
- Track which parts can be returned for credit

**Use case:**
1. Part entered in service ticket
2. Partlog record created with KEY
3. End of period: Query MARCONE AVAILABLE RETURNS matching KEY
4. If match found, part eligible for return
5. Process return, receive credit in MARCONE SALES AND CREDITS

#### 4. ResolvedPn (Part Number Resolution)
**Links:** Partlog.APR ↔ 9999.APR ↔ Stock databases

**Purpose:** Link variant part numbers to standard part numbers

**Use cases:**
- Manufacturer supersedes part number (old → new)
- Multiple manufacturer part numbers for same physical part
- Part number corrections and standardization

**Example:**
- Part entered as "WP12345678-OLD"
- ResolvedPn = "WP12345678-NEW"
- System can find all instances of this part regardless of variant

#### 5. Location References
**Links:** Multiple databases → LOC.APR, DISTINCTLOCATIONS.APR, LOCATION TAGS.APR

**Fields:**
- `TICLOC` in STATUSUPDATE - Ticket location
- `LOCATION` in Partlog - Part storage location

**Purpose:**
- Track where work is done
- Track where parts are stored
- Generate location-based reports
- Calculate stock levels by location

### Reference Database Relationships

```
STATUSUPDATE.APR
    │
    ├─► SHRTMAKE.APR (Manufacturer abbreviations)
    │     Usage: Validate MAKE field, standardize entry
    │
    ├─► STREET NAMES.APR (Address standardization)
    │     Usage: Validate ADDRESS field
    │
    ├─► DISTANCE.APR (Geographic routing)
    │     Usage: Calculate TRIP charges
    │
    ├─► baseissues.APR (Problem codes)
    │     Usage: Standardize SERVICEREQ field
    │
    └─► LOC.APR / LOCATION TAGS.APR (Location codes)
          Usage: Validate TICLOC and LOCATION fields

Partlog.APR
    │
    ├─► PNPDC.APR (Part pricing lookup)
    │     Usage: Validate COST field, standard pricing
    │
    ├─► VENDOR2.APR (Vendor information)
    │     Usage: Validate VENDOR field, track performance
    │
    └─► 9999.APR (Problem parts)
          Usage: ResolvedPn linking for part number resolution
```

---

## Field Definitions and Data Types

### Customer Fields

| Field | Type | Length | Description | Validation |
|-------|------|--------|-------------|------------|
| FIRSTNAME | Text | 50 | Customer first name | Required |
| LASTNAME | Text | 50 | Customer last name | Required |
| ADDRESS | Text | 100 | Street address | Can reference STREET NAMES.APR |
| CITY | Text | 50 | City name | Common: Omaha, Lincoln, Council Bluffs |
| STATE | Text | 2 | State abbreviation | Common: NE, IA |
| ZIP | Numeric/Text | 10 | Zip code | Format: 12345 or 12345-6789 |
| PHONE | Text | 20 | Phone number | Format varies |
| PHTYPE | Text | 10 | Phone type | Values: Home, Work, Mobile, Cell |

### Device/Appliance Fields

| Field | Type | Length | Description | Validation |
|-------|------|--------|-------------|------------|
| MAKE | Text | 50 | Manufacturer name | Can use SHRTMAKE.APR codes |
| TYPE | Text | 20 | Device type | Values: dw, ref, washer, dryer, range, mw |
| MODEL | Text | 50 | Model number | Free text |
| SERIAL | Text | 50 | Serial number | Free text |
| DATEPURCHASED / DATEPUR | Date | - | Purchase date | Optional |

**TYPE Field Values:**
- `dw` = Dishwasher
- `ref` = Refrigerator / Freezer
- `washer` = Washing machine
- `dryer` = Clothes dryer
- `range` = Stove / Oven / Range
- `mw` = Microwave

### Service Fields

| Field | Type | Length | Description | Validation |
|-------|------|--------|-------------|------------|
| SERVICEREQ | Text | 500 | Customer's reported problem | Can use baseissues.APR codes |
| WORKDONE | Text | 500 | Service performed | Free text, be specific |
| NOTES | Text | 1000 | Additional notes | Links to memo.APR |
| STATUS | Text | 20 | Current status | Values vary |
| LOCATION | Text | 20 | Work location code | References LOC.APR |
| TICLOC | Text | 20 | Ticket location | References LOCATION TAGS.APR |

### Date Fields

| Field | Type | Description | Auto-Set | Validation |
|-------|------|-------------|----------|------------|
| DATEIN | Date | Check-in date | Today() on create | Required |
| DATEPROM | Date | Promised completion | DATEIN + 7 days | After DATEIN |
| DATECOMPLT | Date | Actual completion | Manual | Between DATEIN and Today() |
| DATEOUT | Date | Customer pickup | Manual | After DATECOMPLT |
| CREDATE | Date | Record creation date | Today() | System-set |
| CRETIME | Time | Record creation time | CurrTime() | System-set |

**DATECOMPLT Validation Formula:**
```
CUSTDATA.DATECOMPLT = '' OR (CUSTDATA.DATECOMPLT <= Today() AND CUSTDATA.DATECOMPLT >= CUSTDATA.DATEIN)
```

### Parts Fields (Repeated 1-11)

| Field Pattern | Type | Description | Example |
|---------------|------|-------------|---------|
| P1 - P11 | Text (50) | Part name/identifier | "WP12345678" |
| PD1 - PD11 | Text (200) | Part description | "Evaporator fan motor" |
| Q1 - Q11 | Numeric | Quantity used | 1, 2, 3, etc. or '' (empty) |
| C1 - C11 | Currency | Cost per part | $45.00 |

**Critical note on quantities:**
- Set to '' (empty string) not 0 (zero) when clearing
- The `dup` script specifically sets `Q1-Q11 = ''`
- This distinction matters for calculations and reporting

### Financial Fields

| Field | Type | Description | Calculation |
|-------|------|-------------|-------------|
| PARTS | Currency | Total parts cost | Sum of (Q1*C1) + (Q2*C2) + ... + (Q11*C11) |
| REG_LABOR | Currency | Regular labor charge | Manual entry |
| WARR_LABOR | Currency | Warranty labor | Manual entry (often $0 to customer) |
| TRIP | Currency | Trip/travel charge | May reference DISTANCE.APR |
| SHOPSUPPLY | Currency | Shop supplies | Percentage or flat rate |
| OTHER | Currency | Misc charges | Manual entry |
| DEPOSIT | Currency | Deposit/partial payment | Manual entry |
| Grand Total | Currency | Total invoice | PARTS + REG_LABOR + WARR_LABOR + TRIP + SHOPSUPPLY + OTHER - DEPOSIT |
| INVOICE | Text/Numeric (20) | Invoice number | System-generated or manual |
| DLRINVOICE | Text (20) | Dealer invoice | Manual entry |
| HOWPAID | Text (20) | Payment method | Values: Cash, Check, Credit Card, Account, Warranty, Other |

### Partlog Unique Fields

| Field | Type | Length | Description | Formula/Generation |
|-------|------|--------|-------------|-------------------|
| TIMEKEY | Numeric | 14 digits | Unique transaction ID | Year(1) + DayOfYear(3) + Hour(2) + Min(2) + Sec(2) + Random(2) |
| KEY | Text | Variable | Marcone linking composite | Combine(COST, '  ', MAN_INVOIC, '  ', PART_NUM) |
| PART_NUM | Text | 50 | Part number | From P1-P11 in STATUSUPDATE |
| PART_DESCR | Text | 200 | Part description | From PD1-PD11 in STATUSUPDATE |
| COST | Currency | - | Part cost | From C1-C11 in STATUSUPDATE |
| VENDOR | Text | 50 | Supplier name | Typically "Marcone" |
| MAN_INVOIC | Text | 50 | Manufacturer invoice | Supplier invoice number |
| PONUMBER | Text | 50 | Purchase order number | Your PO to supplier |
| RA_NUMBER | Text | 50 | Return authorization | For returns/credits |
| TRACKING | Text | 100 | Shipment tracking | Carrier tracking number |
| DUD | Boolean/Text | 1 | Defective part flag | Y/N or True/False |
| ResolvedPn | Text | 50 | Resolved part number | Links to standard part number |
| ORDCONF | Text | 50 | Order confirmation | Supplier confirmation number |
| COMBO | Text | Variable | Combination field | Various uses |
| PRINT | Boolean | 1 | Print flag | Include on reports |
| LOCUPDATE | Date/Time | - | Location update timestamp | When location changed |
| DATE_OF_RE | Date | - | Date of receipt | When part received from supplier |
| DATEORD | Date | - | Date ordered | When order placed |

---

## Business Operations Insights

### Service Territory
**Geographic Coverage:**
- **Primary cities:** Omaha, Lincoln, Council Bluffs, Bellevue, Fremont
- **States:** Nebraska (NE) and Iowa (IA)
- **Service locations:** 125+ documented in DISTINCTLOCATIONS

**Market characteristics:**
- Multi-location service company
- Residential and commercial appliance repair
- Multiple technicians/service vehicles
- Centralized parts inventory with location-specific stock

### Customer Service Model

**Intake:**
- Phone call or walk-in
- Customer describes problem (SERVICEREQ)
- Device information collected (MAKE, MODEL, SERIAL)
- Promised date set (typically 7 days)

**Service Execution:**
- Diagnosis by technician
- Parts identification and selection
- Repair performed
- Workdone documentation

**Completion:**
- Invoice generation (Final Copy view)
- Customer notification
- Payment collection
- Device return to customer

### Parts Supply Chain

**Primary Supplier: Marcone**
- Major appliance parts distributor
- National coverage
- Next-day delivery common
- Return/credit program available
- Online ordering integration

**Ordering Process:**
1. Part needed identified during service
2. Order placed (MARCONE ORDERS.APR)
3. Confirmation received (ORDCONF field)
4. Shipment tracking (TRACKING field)
5. Receipt (DATE_OF_RE field)
6. Stock update (STOCK ONLY.APR)

**Return Process:**
1. Identify eligible parts (MARCONE AVAILABLE RETURNS.APR via KEY match)
2. Request RA number (RA_NUMBER field)
3. Ship back to Marcone
4. Receive credit (MARCONE SALES AND CREDITS.APR)

**Other supplier programs:**
- **Core parts:** Exchange old compressor/motor for credit (CORES.APR)
- **Loaner units:** Temporary replacements (Loaner.APR)
- **Substitute parts:** Equivalent alternatives when primary unavailable (Subs.APR)

### Inventory Management

**Stock levels:**
- 8,900+ parts tracked
- Multiple storage locations
- 10% increment tracking buckets in DISTINCTLOCATIONS.APR

**Replenishment triggers:**
- Stock ratio analysis (STOCK RATIO.APR)
- Historical demand patterns
- Seasonal adjustments
- Emergency/rush orders

**Organization:**
- Location-based storage (DISTINCTLOCATIONS.APR)
- Manufacturer-based grouping
- Device-type grouping (refrigeration, laundry, cooking, etc.)
- Fast-mover vs. slow-mover segregation

**Optimization:**
- Return excess stock for credit
- Transfer between locations to balance inventory
- Identify obsolete parts
- Monitor part supersessions (ResolvedPn)

### Financial Operations

**Revenue structure:**
- **Parts:** Cost + markup
- **Labor:** Hourly or flat-rate
  - Regular labor (billable)
  - Warranty labor (manufacturer reimbursement)
- **Trip charge:** Distance-based
- **Shop supplies:** Consumables markup
- **Other:** Miscellaneous charges

**Payment methods tracked:**
- Cash
- Check
- Credit card (Visa, Mastercard, Amex, Discover)
- Account/Charge (established customers)
- Warranty (manufacturer-paid)
- Other

**Reporting periods:**
- **Pay period 1:** 1st through 14th of month
- **Pay period 2:** 15th through end of month
- Bi-monthly reporting cycle
- SalesJournal query for revenue by period
- Payments must be "Finalized" to count as revenue

**Financial reconciliation:**
- Match STATUSUPDATE invoices to Payments records
- Reconcile Partlog with MARCONE SALES AND CREDITS
- Identify uncollected payments
- Process returns for credit
- Generate accounting reports via PART EXPORT.APR

### Warranty vs. Retail Service

**Warranty service:**
- WARR_LABOR field used
- Often $0 trip charge to customer
- Parts cost may be covered
- Reimbursement from manufacturer tracked separately
- Customer typically pays nothing or reduced rate

**Retail service:**
- REG_LABOR field used
- Full trip charge applies
- Customer pays all parts costs
- Customer pays in full at completion
- Higher margins

---

## Technical Implementation Details

### LotusScript Technology

**Language:** LotusScript
**Era:** Late 1990s - early 2000s (Lotus Domino/Notes platform)
**Paradigm:** Object-oriented, event-driven
**Similar to:** Visual Basic for Applications (VBA)

**Key language features:**
- Strong typing (Dim variables with types)
- Object model: Application, Database, Document, View, Form, Window
- Event handlers: Click, GotFocus, LostFocus, Change, etc.
- Database API: Query, Find, Sort, Join operations
- String manipulation: Trim, Combine, Left, Right, Mid, Cstr
- Date/Time functions: Today, CurrTime, Year, Month, Day, Hour, Minute, Second, DayOfYear
- Math: Random, arithmetic operators
- Control flow: If/Then/Else, For/Next, While/Wend, Select Case

**Object hierarchy:**
```
Application (top-level)
  └─ Database (APR file)
      ├─ Document (record/row)
      │   └─ Field (column/value)
      ├─ View (form/layout)
      ├─ Query (search/filter)
      └─ Connection (external data)
```

### Database Access Patterns

**Direct field access:**
```lotusscript
CUSTDATA.FIRSTNAME = "John"
CUSTDATA.LASTNAME = "Smith"
```

**Query object:**
```lotusscript
Dim qry As Query
Set qry = New Query
qry.Criteria = "Grand Total > 0"
qry.Execute
```

**FindSort operation:**
```lotusscript
FindSort CUSTDATA By LASTNAME Ascending, FIRSTNAME Ascending
```

**External SQL:**
```lotusscript
Dim conn As Connection
Set conn = connecttodb()
conn.Execute "SELECT * FROM Partlog WHERE VENDOR='Marcone'"
```

### Performance Optimizations

**Indexing strategy:**
- Multiple single-field indexes (PART_NUM, INVOICE, VENDOR, LOCATION, CREDATE)
- Expression-based indexes (TIMEKEY, KEY)
- Covering indexes for common queries

**Indexed fields in Partlog.APR:**
- PART_NUM (frequent lookups by part)
- INVOICE (link to tickets)
- VENDOR (filter by supplier)
- LOCATION (filter by storage location)
- CREDATE (sort by date)
- TRACKING (shipment lookup)
- PONUMBER (purchase order lookup)
- DATE_OF_RE (receipt date)
- MAN_INVOIC (supplier invoice)
- RA_NUMBER (return authorization)
- ORDCONF (order confirmation)
- KEY (Marcone linking - CRITICAL)
- COMBO (combination field)
- PART_DESCR (description search)
- DATEORD (order date)
- PRINT (filter printable)
- DUD (filter defective)

**Performance considerations:**
- 8,900+ parts in database - indexes essential
- Network-based multi-user access (Y:\Lotus shared drive)
- Compression for database maintenance
- Regular compacting to reduce file size
- Backup strategy (Backups folder with dated copies)

### Data Integrity Measures

**Validation formulas:**
- Date range validation on DATECOMPLT
- Required field enforcement
- Data type validation

**Referential integrity:**
- Foreign key relationships via linking fields (INVOICE, KEY, ResolvedPn)
- Orphan record prevention
- Cascade updates via scripts

**Audit trail:**
- CREDATE/CRETIME timestamp on record creation
- memo.APR tracks Created/Modified timestamps for notes
- Can identify dormant tickets (no recent memo modification)

**Backup strategy:**
- Dated backups in Backups folder
- Regular compression before backup
- Database maintenance schedule

### Multi-User Access

**Network location:** `Y:\Lotus` (shared network drive)

**Concurrency control:**
- Record-level locking during edit
- Optimistic concurrency (last-write-wins on conflicts)
- User awareness via status indicators

**Collision avoidance:**
- TIMEKEY includes random component (0-99) for simultaneous part entries
- Unique constraints on key fields

---

## System Files and Documentation

**Location:** `/mnt/c/Users/metro/sp/Lotus documentation/`

### APR Database Files (~50 files)
- STATUSUPDATE.APR
- Partlog.APR
- MARCONE ORDERS.APR
- MARCONE AVAILABLE RETURNS.APR
- MARCONE SALES AND CREDITS.APR
- Marcone tracking.APR
- MARCONE UPDATE.APR
- STOCK ONLY.APR
- STOCK RATIO.APR
- DISTINCTLOCATIONS.APR
- 9999.APR
- CORES.APR
- Loaner.APR
- Subs.APR
- LOC.APR
- LOCATION TAGS.APR
- LOCATION TAG EXPERIMENT.APR
- SHRTMAKE.APR
- STREET NAMES.APR
- LINCOLN STREET NAMES.APR
- DISTANCE.APR
- PNPDC.APR
- baseissues.APR
- CHARTS.APR
- Part and quantity.APR
- PART EXPORT.APR
- PARTBYINVOICE.APR
- SDRATIO.APR
- Table DATA.APR
- VENDOR2.APR
- MicroMnSn.APR
- Payments.APR
- memo.APR
- FINDTRACKING.APR
- DupMarcCredits.APR
- holder.APR
- keeper.APR
- CUSTDATA.ADX (index)
- And ~20+ more

### DBF Data Files (~30 files)
- CUSTDATA.DBF
- Partlog.DBF
- Marcone orders.dbf
- MarcCredits.dbf
- Subs.dbf
- LOC.dbf
- DMI.dbf
- And ~24 more

### ADX Index Files
- Automatically generated for indexed APR/DBF files
- Binary format
- Not directly editable
- One ADX per indexed database

### Documentation Files
- **Table data.txt** - Sample customer call data
- **Lotus reference.txt** - LotusScript function references and 9U5SSH OLE operation notes
- **Version notes** - System change log with:
  - Date: 7/10/25 - Modified KEY field formula
  - Known issue: DATECOMPLT validation during ticket duplication
  - Field linking notes for MARCONE AVAILABLE RETURNS
  - Tagging system development notes

---

## Known Issues and Workarounds

### 1. DATECOMPLT Validation During Duplication
**Issue:** When using `dup` script to duplicate tickets, DATECOMPLT validation formula can trigger errors

**Cause:** Validation checks if DATECOMPLT is between DATEIN and Today(), but during duplication timing can cause conflicts

**Workaround options:**
- Clear DATECOMPLT before running dup
- Temporarily disable validation
- Modify dup script to explicitly handle DATECOMPLT

**Status:** Documented in version notes, awaiting fix

### 2. Field Linking to MARCONE AVAILABLE RETURNS
**Issue:** Challenge linking Partlog to MARCONE AVAILABLE RETURNS accurately

**Solution implemented:** Modified KEY field formula (7/10/25) to use:
```
Combine(Trim(Partlog.COST), '  ', Trim(Partlog.MAN_INVOIC), '  ', Trim(Partlog.PART_NUM))
```

**Status:** Resolved

### 3. Part Number Resolution
**Issue:** Parts tracked with non-claimable field or under different manufacturer numbers

**Solution:** ResolvedPn field in Partlog and 9999.APR database for problem parts

**Process:**
1. Identify problem parts (wrong number, superseded, variant)
2. Add to 9999.APR database
3. Set ResolvedPn to correct/standard part number
4. Queries can now find all variants via ResolvedPn linking

**Status:** Ongoing maintenance required

### 4. Quantity Field Handling
**Issue:** Quantities must be empty string ('') not zero (0) when clearing

**Reason:** Calculations and reports treat '' differently than 0

**Enforcement:** The `dup` script specifically sets `Q1-Q11 = ''`

**Impact:** Custom scripts must follow this convention

### 5. Location Tagging System
**Issue:** Need better organization of storage locations

**Solution in progress:** LOCATION TAG EXPERIMENT.APR testing new tagging approach

**Goal:**
- Hierarchical location organization
- Better grouping for inventory reports
- Faster location-based queries

**Status:** Experimental, not yet in production

---

## Future Enhancements Noted

### From Documentation Analysis:

1. **Improved location tagging** (LOCATION TAG EXPERIMENT.APR in development)
2. **Better MARCONE AVAILABLE RETURNS linking** (partially addressed with KEY formula change)
3. **Non-claimable parts tracking** (workaround via ResolvedPn, could be formalized)
4. **Fix DATECOMPLT validation issue** during duplication
5. **MySQL integration** (evidence of attempted connection to 192.168.1.30 - internal server)
6. **Web interface** (Flask app at app.py:1 suggests modernization effort)

---

## Summary

This Lotus Approach system represents a **comprehensive, battle-tested field service management solution** for a multi-location appliance repair company. The system handles:

✅ **Complete ticket lifecycle** from intake to completion to payment
✅ **Sophisticated parts tracking** with supplier integration
✅ **Multi-location inventory management** with 8,900+ parts
✅ **Financial reporting** by pay period with SalesJournal
✅ **Supplier reconciliation** for returns and credits
✅ **Extensive automation** via LotusScript macros
✅ **Validated data entry** with business rules
✅ **Audit trails** with timestamps
✅ **Multi-user network access**

The system shows evidence of continuous improvement (version notes, experimental features) and integration with modern web technologies (Flask app), indicating an organization committed to both maintaining legacy functionality and modernizing where beneficial.

**Key success factors:**
- Well-designed data structures with appropriate indexes
- Smart linking via TIMEKEY and KEY fields
- Automation reducing data entry errors (dup script, focus navigation, date handling)
- Clear separation between warranty and retail service
- Integration with major parts supplier (Marcone)
- Bi-monthly financial reporting aligned with business cycles
- Multi-location stock management for efficient inventory

This is production-ready, business-critical software serving real daily operations.
