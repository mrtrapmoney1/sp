"""
Ticket Model

Represents service tickets/work orders from the CUSTDATA.DBF table.
This is the primary record for tracking customer service calls from
intake through completion and payment.
"""

from datetime import datetime
from typing import Optional
from ..extensions import db


class Ticket(db.Model):
    """
    Service ticket model representing a customer work order.

    Maps to the CUSTDATA.DBF structure from the Lotus Approach system.
    Contains customer information, device details, service records,
    parts used, and financial information.
    """

    __tablename__ = 'tickets'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Invoice/Reference numbers
    invoice = db.Column(db.String(20), unique=True, nullable=False, index=True)
    dlr_invoice = db.Column(db.String(17), index=True)  # ServicePower CallNumber

    # Customer information
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50), index=True)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50), index=True)
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10), index=True)
    phone = db.Column(db.String(20))
    phone2 = db.Column(db.String(20))
    phone_type = db.Column(db.String(10))  # Home, Work, Mobile, Cell

    # Device/Appliance information
    make = db.Column(db.String(50), index=True)
    typ = db.Column(db.String(20), index=True)  # dw, ref, washer, dryer, range, mw
    model = db.Column(db.String(50), index=True)
    serial = db.Column(db.String(50))
    date_purchased = db.Column(db.Date)

    # Service information
    service_req = db.Column(db.Text)  # Customer's reported problem
    work_done = db.Column(db.Text)  # Technician's description
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open', index=True)
    location = db.Column(db.String(20))  # Storage/work location code
    tic_loc = db.Column(db.String(25))  # Ticket location identifier

    # Date tracking
    date_in = db.Column(db.Date, default=datetime.utcnow, index=True)
    date_promised = db.Column(db.Date)
    date_completed = db.Column(db.Date, index=True)
    date_out = db.Column(db.Date)

    # Parts used (11 slots matching Lotus structure)
    # Part 1
    p1 = db.Column(db.String(50))
    pd1 = db.Column(db.String(200))
    q1 = db.Column(db.Integer)
    c1 = db.Column(db.Numeric(10, 2))
    # Part 2
    p2 = db.Column(db.String(50))
    pd2 = db.Column(db.String(200))
    q2 = db.Column(db.Integer)
    c2 = db.Column(db.Numeric(10, 2))
    # Part 3
    p3 = db.Column(db.String(50))
    pd3 = db.Column(db.String(200))
    q3 = db.Column(db.Integer)
    c3 = db.Column(db.Numeric(10, 2))
    # Part 4
    p4 = db.Column(db.String(50))
    pd4 = db.Column(db.String(200))
    q4 = db.Column(db.Integer)
    c4 = db.Column(db.Numeric(10, 2))
    # Part 5
    p5 = db.Column(db.String(50))
    pd5 = db.Column(db.String(200))
    q5 = db.Column(db.Integer)
    c5 = db.Column(db.Numeric(10, 2))
    # Part 6
    p6 = db.Column(db.String(50))
    pd6 = db.Column(db.String(200))
    q6 = db.Column(db.Integer)
    c6 = db.Column(db.Numeric(10, 2))
    # Part 7
    p7 = db.Column(db.String(50))
    pd7 = db.Column(db.String(200))
    q7 = db.Column(db.Integer)
    c7 = db.Column(db.Numeric(10, 2))
    # Part 8
    p8 = db.Column(db.String(50))
    pd8 = db.Column(db.String(200))
    q8 = db.Column(db.Integer)
    c8 = db.Column(db.Numeric(10, 2))
    # Part 9
    p9 = db.Column(db.String(50))
    pd9 = db.Column(db.String(200))
    q9 = db.Column(db.Integer)
    c9 = db.Column(db.Numeric(10, 2))
    # Part 10
    p10 = db.Column(db.String(50))
    pd10 = db.Column(db.String(200))
    q10 = db.Column(db.Integer)
    c10 = db.Column(db.Numeric(10, 2))
    # Part 11
    p11 = db.Column(db.String(50))
    pd11 = db.Column(db.String(200))
    q11 = db.Column(db.Integer)
    c11 = db.Column(db.Numeric(10, 2))

    # Financial fields
    parts_total = db.Column(db.Numeric(10, 2), default=0)
    reg_labor = db.Column(db.Numeric(10, 2), default=0)
    warr_labor = db.Column(db.Numeric(10, 2), default=0)
    trip = db.Column(db.Numeric(10, 2), default=0)
    shop_supply = db.Column(db.Numeric(10, 2), default=0)
    other = db.Column(db.Numeric(10, 2), default=0)
    deposit = db.Column(db.Numeric(10, 2), default=0)
    grand_total = db.Column(db.Numeric(10, 2), default=0)
    how_paid = db.Column(db.String(20))  # Cash, Check, Credit Card, Account, Warranty

    # Warranty/Accessor information
    warranty_type = db.Column(db.String(10))  # IW, SC, etc.
    accessor = db.Column(db.String(150))

    # ServicePower reference fields
    sp_call_number = db.Column(db.String(30), index=True)
    sp_fss_call_id = db.Column(db.String(30))
    sp_mfg_id = db.Column(db.String(30))

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payment = db.relationship('Payment', backref='ticket', uselist=False, lazy='joined')
    parts_history = db.relationship('PartsHistory', backref='ticket', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Ticket {self.invoice}: {self.lastname}, {self.firstname}>'

    def calculate_parts_total(self) -> float:
        """Calculate total parts cost from individual part entries."""
        total = 0
        for i in range(1, 12):
            qty = getattr(self, f'q{i}', None)
            cost = getattr(self, f'c{i}', None)
            if qty and cost:
                total += qty * float(cost)
        return total

    def calculate_grand_total(self) -> float:
        """Calculate grand total of all charges minus deposit."""
        parts = float(self.parts_total or 0)
        reg = float(self.reg_labor or 0)
        warr = float(self.warr_labor or 0)
        trip = float(self.trip or 0)
        shop = float(self.shop_supply or 0)
        other = float(self.other or 0)
        deposit = float(self.deposit or 0)
        return parts + reg + warr + trip + shop + other - deposit

    def get_parts_list(self) -> list:
        """Get list of all parts used in this ticket."""
        parts = []
        for i in range(1, 12):
            part_num = getattr(self, f'p{i}', None)
            if part_num:
                parts.append({
                    'part_number': part_num,
                    'description': getattr(self, f'pd{i}', ''),
                    'quantity': getattr(self, f'q{i}', 0),
                    'cost': float(getattr(self, f'c{i}', 0) or 0),
                })
        return parts

    def to_dict(self) -> dict:
        """Convert ticket to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'invoice': self.invoice,
            'dlr_invoice': self.dlr_invoice,
            'customer': {
                'firstname': self.firstname,
                'lastname': self.lastname,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'zip': self.zip,
                'phone': self.phone,
                'phone2': self.phone2,
            },
            'device': {
                'make': self.make,
                'type': self.typ,
                'model': self.model,
                'serial': self.serial,
                'date_purchased': self.date_purchased.isoformat() if self.date_purchased else None,
            },
            'service': {
                'service_req': self.service_req,
                'work_done': self.work_done,
                'notes': self.notes,
                'status': self.status,
                'location': self.location,
            },
            'dates': {
                'date_in': self.date_in.isoformat() if self.date_in else None,
                'date_promised': self.date_promised.isoformat() if self.date_promised else None,
                'date_completed': self.date_completed.isoformat() if self.date_completed else None,
                'date_out': self.date_out.isoformat() if self.date_out else None,
            },
            'parts': self.get_parts_list(),
            'financial': {
                'parts_total': float(self.parts_total or 0),
                'reg_labor': float(self.reg_labor or 0),
                'warr_labor': float(self.warr_labor or 0),
                'trip': float(self.trip or 0),
                'shop_supply': float(self.shop_supply or 0),
                'other': float(self.other or 0),
                'deposit': float(self.deposit or 0),
                'grand_total': float(self.grand_total or 0),
                'how_paid': self.how_paid,
            },
            'servicepower': {
                'call_number': self.sp_call_number,
                'fss_call_id': self.sp_fss_call_id,
                'mfg_id': self.sp_mfg_id,
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
