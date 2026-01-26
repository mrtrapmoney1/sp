"""
Parts History Model

Represents parts transaction records from the Partlog.DBF table.
Tracks every part from order through receipt, stock, installation,
and potential return. Uses the TIMEKEY pattern for unique identification.
"""

from datetime import datetime
from typing import Optional
import random
from ..extensions import db


class PartsHistory(db.Model):
    """
    Parts history model representing individual part transactions.

    Maps to the Partlog.DBF structure from the Lotus Approach system.
    Each record tracks a part through its lifecycle including ordering,
    receipt, installation, and return eligibility.
    """

    __tablename__ = 'parts_history'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # TIMEKEY - Unique 14-digit identifier
    # Formula: Year(1) + DayOfYear(3) + Hour(2) + Min(2) + Sec(2) + Random(2)
    timekey = db.Column(db.BigInteger, unique=True, nullable=False, index=True)

    # Part identification
    part_num = db.Column(db.String(50), nullable=False, index=True)
    part_descr = db.Column(db.String(200), index=True)
    vendor = db.Column(db.String(50), index=True, default='Marcone')

    # Financial information
    cost = db.Column(db.Numeric(10, 2))
    invoice = db.Column(db.String(20), index=True)  # Internal invoice (FK to tickets)
    man_invoic = db.Column(db.String(50), index=True)  # Manufacturer/supplier invoice
    po_number = db.Column(db.String(50), index=True)  # Purchase order number

    # Location and storage
    location = db.Column(db.String(20), index=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)

    # Tracking information
    tracking = db.Column(db.String(100), index=True)
    ra_number = db.Column(db.String(50), index=True)  # Return authorization
    ord_conf = db.Column(db.String(50), index=True)  # Order confirmation
    is_dud = db.Column(db.Boolean, default=False, index=True)  # Defective part flag

    # Dates
    date_ordered = db.Column(db.Date, index=True)
    date_received = db.Column(db.Date, index=True)
    loc_update = db.Column(db.DateTime)  # Location update timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_time = db.Column(db.Time)

    # KEY field for Marcone linking
    # Formula: Combine(COST, '  ', MAN_INVOIC, '  ', PART_NUM)
    marcone_key = db.Column(db.String(150), index=True)

    # COMBO field (combination field for various uses)
    combo = db.Column(db.String(100), index=True)

    # ResolvedPn - Links variant part numbers to standard/superseded part numbers
    resolved_pn = db.Column(db.String(50), index=True)

    # Print flag - controls whether part appears on reports
    should_print = db.Column(db.Boolean, default=True, index=True)

    # Foreign key to ticket
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=True)

    # Quantity used (from Q1-Q11 in original)
    quantity = db.Column(db.Integer, default=1)

    def __repr__(self) -> str:
        return f'<PartsHistory {self.timekey}: {self.part_num}>'

    @staticmethod
    def generate_timekey() -> int:
        """
        Generate a unique TIMEKEY using the Lotus formula.

        Formula:
            Right(Year(Today()), 1) * 100000000000 +
            DayOfYear(Today()) * 100000000 +
            Hour(CurrTime()) * 1000000 +
            Minute(CurrTime()) * 10000 +
            Second(CurrTime()) * 100 +
            (Random() * 99)

        Returns:
            14-digit unique identifier
        """
        now = datetime.now()
        year_digit = now.year % 10  # Last digit of year
        day_of_year = now.timetuple().tm_yday  # Day 1-366
        hour = now.hour
        minute = now.minute
        second = now.second
        random_part = random.randint(0, 99)

        timekey = (
            year_digit * 100000000000 +
            day_of_year * 100000000 +
            hour * 1000000 +
            minute * 10000 +
            second * 100 +
            random_part
        )
        return timekey

    @staticmethod
    def generate_marcone_key(cost: float, man_invoic: str, part_num: str) -> str:
        """
        Generate the KEY field for Marcone linking.

        Formula: Combine(Trim(COST), '  ', Trim(MAN_INVOIC), '  ', Trim(PART_NUM))

        Args:
            cost: Part cost
            man_invoic: Manufacturer invoice number
            part_num: Part number

        Returns:
            Composite key string for Marcone matching
        """
        cost_str = f'{cost:.2f}' if cost else ''
        man_invoic_str = (man_invoic or '').strip()
        part_num_str = (part_num or '').strip()
        return f'{cost_str}  {man_invoic_str}  {part_num_str}'

    def update_marcone_key(self) -> None:
        """Update the Marcone key based on current field values."""
        self.marcone_key = self.generate_marcone_key(
            float(self.cost) if self.cost else 0,
            self.man_invoic,
            self.part_num
        )

    def to_dict(self) -> dict:
        """Convert parts history to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'timekey': self.timekey,
            'part_num': self.part_num,
            'part_descr': self.part_descr,
            'vendor': self.vendor,
            'cost': float(self.cost) if self.cost else None,
            'invoice': self.invoice,
            'man_invoic': self.man_invoic,
            'po_number': self.po_number,
            'location': self.location,
            'tracking': self.tracking,
            'ra_number': self.ra_number,
            'ord_conf': self.ord_conf,
            'is_dud': self.is_dud,
            'date_ordered': self.date_ordered.isoformat() if self.date_ordered else None,
            'date_received': self.date_received.isoformat() if self.date_received else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'marcone_key': self.marcone_key,
            'resolved_pn': self.resolved_pn,
            'quantity': self.quantity,
            'ticket_id': self.ticket_id,
        }

    @classmethod
    def create_from_ticket_part(
        cls,
        ticket_id: int,
        invoice: str,
        part_num: str,
        part_descr: str,
        quantity: int,
        cost: float,
        location: str = None,
        vendor: str = 'Marcone'
    ) -> 'PartsHistory':
        """
        Create a new parts history record from ticket part data.

        This mimics the automatic record creation that happens in the
        Lotus system when parts are entered in STATUSUPDATE.

        Args:
            ticket_id: ID of the parent ticket
            invoice: Invoice number from ticket
            part_num: Part number (P1-P11)
            part_descr: Part description (PD1-PD11)
            quantity: Quantity used (Q1-Q11)
            cost: Cost per part (C1-C11)
            location: Storage location
            vendor: Supplier name (default 'Marcone')

        Returns:
            New PartsHistory instance (not yet committed)
        """
        now = datetime.now()
        record = cls(
            timekey=cls.generate_timekey(),
            part_num=part_num,
            part_descr=part_descr,
            vendor=vendor,
            cost=cost,
            invoice=invoice,
            location=location,
            quantity=quantity,
            ticket_id=ticket_id,
            created_at=now,
            created_time=now.time(),
        )
        record.update_marcone_key()
        return record
