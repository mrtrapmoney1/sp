#!/usr/bin/env python3
"""
DBF to PostgreSQL Migration Script

Migrates data from legacy dBase IV files to the new PostgreSQL database.
Processes files in batches for memory efficiency.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from dbfread import DBF

from app import create_app
from app.extensions import db
from app.models import (
    Ticket, PartsHistory, Payment, Location, Inventory,
    SupplierReturn, SupplierCredit
)


# Configuration
DBF_BASE_PATH = 'data/lotus-database'
BATCH_SIZE = 1000

# DBF file mappings
DBF_FILES = {
    'locations': 'LOC.dbf',
    'tickets': 'CUSTDATA.dbf',
    'parts_history': 'Partlog.dbf',
    'payments': 'payments.dbf',
    'inventory': 'STOCK ONLY.dbf',
    'supplier_returns': 'MARCONE RETURN.dbf',
    'supplier_credits': 'MarcCredits.dbf',
}


def read_dbf(filename: str) -> List[Dict[str, Any]]:
    """
    Read a DBF file and return records as list of dicts.

    Args:
        filename: DBF filename relative to DBF_BASE_PATH

    Returns:
        List of record dictionaries
    """
    filepath = os.path.join(DBF_BASE_PATH, filename)

    if not os.path.exists(filepath):
        print(f"  Warning: File not found: {filepath}")
        return []

    try:
        table = DBF(filepath, load=True, ignore_missing_memofile=True)
        records = list(table)
        print(f"  Read {len(records)} records from {filename}")
        return records
    except Exception as e:
        print(f"  Error reading {filename}: {e}")
        return []


def clean_string(value: Any, max_length: int = None) -> Optional[str]:
    """Clean and optionally truncate a string value."""
    if value is None:
        return None
    s = str(value).strip()
    if s == '' or s.lower() in ('none', 'nan'):
        return None
    if max_length:
        s = s[:max_length]
    return s


def parse_date(value: Any) -> Optional[datetime]:
    """Parse a date value from DBF."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() in ('none', 'nan'):
            return None
        # Try common formats
        for fmt in ['%Y%m%d', '%m/%d/%Y', '%Y-%m-%d']:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def migrate_locations(records: List[Dict]) -> int:
    """Migrate location records."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                loc = Location(
                    code=clean_string(rec.get('CODE'), 10),
                    name=clean_string(rec.get('NAME'), 50),
                    address=clean_string(rec.get('ADDRESS'), 100),
                    city=clean_string(rec.get('CITY'), 50),
                    state=clean_string(rec.get('STATE'), 2),
                    zip_code=clean_string(rec.get('ZIP'), 10),
                    phone=clean_string(rec.get('PHONE'), 20),
                    latitude=rec.get('LAT'),
                    longitude=rec.get('LNG')
                )
                db.session.add(loc)
                count += 1
            except Exception as e:
                print(f"    Error migrating location: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def migrate_tickets(records: List[Dict]) -> int:
    """Migrate ticket/customer records from CUSTDATA."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                ticket = Ticket(
                    invoice=clean_string(rec.get('INVOICE'), 10),
                    lastname=clean_string(rec.get('LASTNAME'), 25),
                    firstname=clean_string(rec.get('FIRSTNAME'), 15),
                    address=clean_string(rec.get('ADDRESS'), 25),
                    city=clean_string(rec.get('CITY'), 30),
                    state=clean_string(rec.get('STATE'), 2),
                    zip=clean_string(rec.get('ZIP'), 5),
                    phone=clean_string(rec.get('PHONE'), 12),
                    phone2=clean_string(rec.get('PHONE2'), 12),
                    location=clean_string(rec.get('LOCATION'), 15),
                    service_req=clean_string(rec.get('SERVICEREQ'), 250),
                    make=clean_string(rec.get('MAKE'), 15),
                    typ=clean_string(rec.get('TYP') or rec.get('TYP 0'), 15),
                    model=clean_string(rec.get('MODEL'), 20),
                    serial=clean_string(rec.get('SERIAL'), 26),
                    date_in=parse_date(rec.get('DATEIN')),
                    date_purchased=parse_date(rec.get('DATEPUR')),
                    sp_call_number=clean_string(rec.get('BTADDRESS'), 30),
                    accessor=clean_string(rec.get('ACCESSOR'), 150),
                    tic_loc=clean_string(rec.get('TICLOC'), 25),
                    dlr_invoice=clean_string(rec.get('DLRINVOICE'), 17),
                )
                db.session.add(ticket)
                count += 1
            except Exception as e:
                print(f"    Error migrating ticket: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def migrate_parts_history(records: List[Dict]) -> int:
    """Migrate parts history from Partlog."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                parts = PartsHistory(
                    timekey=clean_string(rec.get('TIMEKEY'), 14),
                    make=clean_string(rec.get('MAKE'), 15),
                    model=clean_string(rec.get('MODEL'), 20),
                    symptom=clean_string(rec.get('SYMPT') or rec.get('SERVICEREQ'), 250),
                    part_number_1=clean_string(rec.get('P1'), 30),
                    part_desc_1=clean_string(rec.get('PD1'), 50),
                    part_number_2=clean_string(rec.get('P2'), 30),
                    part_desc_2=clean_string(rec.get('PD2'), 50),
                    part_number_3=clean_string(rec.get('P3'), 30),
                    part_desc_3=clean_string(rec.get('PD3'), 50),
                    service_date=parse_date(rec.get('DATE'))
                )
                db.session.add(parts)
                count += 1
            except Exception as e:
                print(f"    Error migrating parts history: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def migrate_payments(records: List[Dict]) -> int:
    """Migrate payment records."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                payment = Payment(
                    invoice=clean_string(rec.get('INVOICE'), 10),
                    amount=rec.get('AMOUNT'),
                    payment_type=clean_string(rec.get('PAYTYPE') or rec.get('TYPE'), 20),
                    payment_date=parse_date(rec.get('PAYDATE') or rec.get('DATE')),
                    finalized_at=parse_date(rec.get('FINALIZED')),
                    notes=clean_string(rec.get('NOTES'), 250)
                )
                db.session.add(payment)
                count += 1
            except Exception as e:
                print(f"    Error migrating payment: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def migrate_inventory(records: List[Dict]) -> int:
    """Migrate inventory records."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                inv = Inventory(
                    part_number=clean_string(rec.get('PARTNO') or rec.get('PART'), 30),
                    description=clean_string(rec.get('DESC') or rec.get('DESCRIPTION'), 100),
                    quantity=rec.get('QTY') or rec.get('QUANTITY') or 0,
                    location_code=clean_string(rec.get('LOC') or rec.get('LOCATION'), 10),
                    bin_location=clean_string(rec.get('BIN'), 20),
                    cost=rec.get('COST'),
                    price=rec.get('PRICE')
                )
                db.session.add(inv)
                count += 1
            except Exception as e:
                print(f"    Error migrating inventory: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def migrate_supplier_returns(records: List[Dict]) -> int:
    """Migrate supplier return records."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                ret = SupplierReturn(
                    return_number=clean_string(rec.get('RETNO') or rec.get('RETURN_NO'), 20),
                    part_number=clean_string(rec.get('PART') or rec.get('PARTNO'), 30),
                    description=clean_string(rec.get('DESC'), 100),
                    status=clean_string(rec.get('STATUS'), 20),
                    credit_amount=rec.get('CREDIT'),
                    return_date=parse_date(rec.get('DATE') or rec.get('RETDATE')),
                    notes=clean_string(rec.get('NOTES'), 250)
                )
                db.session.add(ret)
                count += 1
            except Exception as e:
                print(f"    Error migrating supplier return: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def migrate_supplier_credits(records: List[Dict]) -> int:
    """Migrate supplier credit records."""
    count = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        for rec in batch:
            try:
                credit = SupplierCredit(
                    credit_number=clean_string(rec.get('CREDITNO') or rec.get('CREDIT_NO'), 20),
                    invoice=clean_string(rec.get('INVOICE'), 20),
                    amount=rec.get('AMOUNT'),
                    credit_date=parse_date(rec.get('DATE') or rec.get('CREDITDATE')),
                    applied=rec.get('APPLIED') == 'Y' if rec.get('APPLIED') else False,
                    notes=clean_string(rec.get('NOTES'), 250)
                )
                db.session.add(credit)
                count += 1
            except Exception as e:
                print(f"    Error migrating supplier credit: {e}")

        db.session.commit()
        print(f"    Migrated batch {i // BATCH_SIZE + 1}")

    return count


def main():
    """Run the migration."""
    print("=" * 60)
    print("DBF to PostgreSQL Migration")
    print("=" * 60)

    # Create Flask app context
    app = create_app('development')

    with app.app_context():
        # Migration order (respects foreign key dependencies)
        migrations = [
            ('locations', DBF_FILES.get('locations'), migrate_locations),
            ('tickets', DBF_FILES.get('tickets'), migrate_tickets),
            ('parts_history', DBF_FILES.get('parts_history'), migrate_parts_history),
            ('payments', DBF_FILES.get('payments'), migrate_payments),
            ('inventory', DBF_FILES.get('inventory'), migrate_inventory),
            ('supplier_returns', DBF_FILES.get('supplier_returns'), migrate_supplier_returns),
            ('supplier_credits', DBF_FILES.get('supplier_credits'), migrate_supplier_credits),
        ]

        total_migrated = 0

        for name, filename, migrate_func in migrations:
            if not filename:
                print(f"\nSkipping {name}: No file configured")
                continue

            print(f"\n{'=' * 40}")
            print(f"Migrating: {name}")
            print(f"{'=' * 40}")

            records = read_dbf(filename)

            if records:
                try:
                    count = migrate_func(records)
                    total_migrated += count
                    print(f"  Successfully migrated {count} {name} records")
                except Exception as e:
                    print(f"  Migration failed: {e}")
                    db.session.rollback()
            else:
                print(f"  No records to migrate")

        print(f"\n{'=' * 60}")
        print(f"Migration Complete!")
        print(f"Total records migrated: {total_migrated}")
        print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
