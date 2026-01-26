"""
Supplier Models

Represents supplier-related records including returns and credits
from the MARCONE AVAILABLE RETURNS.APR and MARCONE SALES AND CREDITS.APR tables.
"""

from datetime import datetime
from typing import Optional, List
from ..extensions import db


class SupplierReturn(db.Model):
    """
    Supplier return model representing parts eligible for return credit.

    Maps to the MARCONE AVAILABLE RETURNS.APR structure from the
    Lotus Approach system. Uses the KEY field for matching to Partlog records.
    """

    __tablename__ = 'supplier_returns'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # KEY field for Marcone linking
    # Formula: Combine(COST, '  ', MAN_INVOIC, '  ', PART_NUM)
    marcone_key = db.Column(db.String(150), nullable=False, index=True)

    # Part information
    part_num = db.Column(db.String(50), nullable=False, index=True)
    part_descr = db.Column(db.String(200))
    cost = db.Column(db.Numeric(10, 2))

    # Invoice references
    invoice = db.Column(db.String(20), index=True)  # Internal invoice
    man_invoic = db.Column(db.String(50), index=True)  # Manufacturer invoice

    # Return information
    ra_number = db.Column(db.String(50), index=True)  # Return authorization
    return_reason = db.Column(db.String(100))
    return_quantity = db.Column(db.Integer, default=1)

    # Status
    status = db.Column(db.String(20), default='Eligible', index=True)
    # Eligible, Requested, Approved, Shipped, Credited, Denied

    # Dates
    eligible_date = db.Column(db.Date, index=True)
    requested_date = db.Column(db.Date)
    shipped_date = db.Column(db.Date)
    credited_date = db.Column(db.Date)

    # Credit information (filled when credit received)
    credit_amount = db.Column(db.Numeric(10, 2))
    credit_reference = db.Column(db.String(50))

    # Vendor (default Marcone)
    vendor = db.Column(db.String(50), default='Marcone', index=True)

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<SupplierReturn {self.part_num}: {self.status}>'

    def request_return(self, reason: str = None) -> None:
        """
        Request return authorization.

        Args:
            reason: Reason for return
        """
        self.status = 'Requested'
        self.requested_date = datetime.utcnow().date()
        if reason:
            self.return_reason = reason

    def approve_return(self, ra_number: str) -> None:
        """
        Mark return as approved with RA number.

        Args:
            ra_number: Return authorization number from supplier
        """
        self.status = 'Approved'
        self.ra_number = ra_number

    def mark_shipped(self) -> None:
        """Mark return as shipped to supplier."""
        self.status = 'Shipped'
        self.shipped_date = datetime.utcnow().date()

    def apply_credit(self, credit_amount: float, reference: str = None) -> None:
        """
        Apply credit from supplier.

        Args:
            credit_amount: Amount of credit received
            reference: Credit reference number
        """
        self.status = 'Credited'
        self.credited_date = datetime.utcnow().date()
        self.credit_amount = credit_amount
        if reference:
            self.credit_reference = reference

    def deny_return(self, reason: str = None) -> None:
        """
        Mark return as denied.

        Args:
            reason: Reason for denial
        """
        self.status = 'Denied'
        if reason:
            self.return_reason = reason

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'marcone_key': self.marcone_key,
            'part_num': self.part_num,
            'part_descr': self.part_descr,
            'cost': float(self.cost) if self.cost else None,
            'invoice': self.invoice,
            'man_invoic': self.man_invoic,
            'ra_number': self.ra_number,
            'return_reason': self.return_reason,
            'return_quantity': self.return_quantity,
            'status': self.status,
            'eligible_date': self.eligible_date.isoformat() if self.eligible_date else None,
            'requested_date': self.requested_date.isoformat() if self.requested_date else None,
            'shipped_date': self.shipped_date.isoformat() if self.shipped_date else None,
            'credited_date': self.credited_date.isoformat() if self.credited_date else None,
            'credit_amount': float(self.credit_amount) if self.credit_amount else None,
            'credit_reference': self.credit_reference,
            'vendor': self.vendor,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def find_by_marcone_key(cls, key: str) -> Optional['SupplierReturn']:
        """Find return eligibility by Marcone key."""
        return cls.query.filter_by(marcone_key=key).first()

    @classmethod
    def get_eligible_returns(cls, vendor: str = 'Marcone') -> List['SupplierReturn']:
        """Get all parts currently eligible for return."""
        return cls.query.filter_by(
            vendor=vendor,
            status='Eligible'
        ).order_by(cls.eligible_date.desc()).all()


class SupplierCredit(db.Model):
    """
    Supplier credit model representing credits received from supplier.

    Maps to the MARCONE SALES AND CREDITS.APR structure from the
    Lotus Approach system. Tracks financial transactions with suppliers.
    """

    __tablename__ = 'supplier_credits'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # KEY field for linking (same format as SupplierReturn)
    marcone_key = db.Column(db.String(150), index=True)

    # Transaction type
    transaction_type = db.Column(db.String(20), nullable=False, index=True)
    # Sale, Credit, Adjustment, Return

    # References
    invoice = db.Column(db.String(20), index=True)  # Internal invoice
    man_invoic = db.Column(db.String(50), index=True)  # Supplier invoice/credit memo
    ra_number = db.Column(db.String(50), index=True)  # Return authorization

    # Part information (for credits related to specific parts)
    part_num = db.Column(db.String(50), index=True)
    part_descr = db.Column(db.String(200))
    quantity = db.Column(db.Integer)

    # Financial
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_credit = db.Column(db.Boolean, default=True)  # True=credit, False=charge

    # Dates
    transaction_date = db.Column(db.Date, nullable=False, index=True)

    # Vendor
    vendor = db.Column(db.String(50), default='Marcone', index=True)

    # Status
    is_reconciled = db.Column(db.Boolean, default=False, index=True)
    reconciled_date = db.Column(db.Date)

    # Notes
    notes = db.Column(db.Text)

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        credit_str = 'CR' if self.is_credit else 'DR'
        return f'<SupplierCredit {credit_str} ${self.amount}: {self.transaction_type}>'

    def reconcile(self) -> None:
        """Mark transaction as reconciled."""
        self.is_reconciled = True
        self.reconciled_date = datetime.utcnow().date()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'marcone_key': self.marcone_key,
            'transaction_type': self.transaction_type,
            'invoice': self.invoice,
            'man_invoic': self.man_invoic,
            'ra_number': self.ra_number,
            'part_num': self.part_num,
            'part_descr': self.part_descr,
            'quantity': self.quantity,
            'amount': float(self.amount) if self.amount else None,
            'is_credit': self.is_credit,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'vendor': self.vendor,
            'is_reconciled': self.is_reconciled,
            'reconciled_date': self.reconciled_date.isoformat() if self.reconciled_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_unreconciled(
        cls,
        vendor: str = 'Marcone',
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List['SupplierCredit']:
        """
        Get unreconciled transactions for a vendor.

        Args:
            vendor: Vendor name
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of unreconciled SupplierCredit records
        """
        query = cls.query.filter_by(
            vendor=vendor,
            is_reconciled=False
        )

        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)

        return query.order_by(cls.transaction_date.desc()).all()

    @classmethod
    def get_period_summary(
        cls,
        vendor: str,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """
        Get credit/debit summary for a period.

        Args:
            vendor: Vendor name
            start_date: Period start date
            end_date: Period end date

        Returns:
            Dictionary with total_credits, total_charges, net_amount
        """
        from sqlalchemy import func

        credits = db.session.query(func.sum(cls.amount)).filter(
            cls.vendor == vendor,
            cls.transaction_date >= start_date,
            cls.transaction_date <= end_date,
            cls.is_credit == True
        ).scalar() or 0

        charges = db.session.query(func.sum(cls.amount)).filter(
            cls.vendor == vendor,
            cls.transaction_date >= start_date,
            cls.transaction_date <= end_date,
            cls.is_credit == False
        ).scalar() or 0

        return {
            'total_credits': float(credits),
            'total_charges': float(charges),
            'net_amount': float(credits) - float(charges),
        }
