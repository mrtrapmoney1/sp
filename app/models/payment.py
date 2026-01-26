"""
Payment Model

Represents payment records from the Payments.APR table.
Tracks payment information and the critical finalized_at timestamp
which determines when a payment counts as revenue for reporting.
"""

from datetime import datetime
from typing import Optional
from ..extensions import db


class Payment(db.Model):
    """
    Payment model representing a payment record.

    Maps to the Payments.APR structure from the Lotus Approach system.
    The finalized_at field is critical for SalesJournal queries which
    determine revenue by pay period.
    """

    __tablename__ = 'payments'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key to ticket
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)

    # Invoice reference (matches ticket invoice)
    invoice = db.Column(db.String(20), nullable=False, index=True)

    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20))  # Cash, Check, Credit Card, Account, Warranty
    reference_number = db.Column(db.String(50))  # Check number, CC auth, etc.

    # Status
    status = db.Column(db.String(20), default='Pending', index=True)  # Pending, Finalized, Refunded

    # Finalize timestamp - CRITICAL for SalesJournal reporting
    # Query: Grand Total > 0 AND Payments.Finalize BETWEEN [start] AND [end]
    finalized_at = db.Column(db.DateTime, index=True)

    # Notes
    notes = db.Column(db.Text)

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Payment {self.invoice}: ${self.amount}>'

    def finalize(self) -> None:
        """
        Finalize the payment by setting the finalized_at timestamp.

        This timestamp is used in SalesJournal queries to determine
        which payments count as revenue for a given pay period.
        """
        self.finalized_at = datetime.utcnow()
        self.status = 'Finalized'

    def refund(self, reason: str = None) -> None:
        """
        Mark payment as refunded.

        Args:
            reason: Optional reason for refund
        """
        self.status = 'Refunded'
        if reason:
            self.notes = (self.notes or '') + f'\nRefund reason: {reason}'
        self.updated_at = datetime.utcnow()

    def is_finalized(self) -> bool:
        """Check if payment has been finalized."""
        return self.finalized_at is not None

    def to_dict(self) -> dict:
        """Convert payment to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'invoice': self.invoice,
            'amount': float(self.amount) if self.amount else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'status': self.status,
            'finalized_at': self.finalized_at.isoformat() if self.finalized_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_sales_journal(
        cls,
        start_date: datetime,
        end_date: datetime
    ) -> list:
        """
        Get finalized payments for SalesJournal reporting.

        This replicates the Lotus SalesJournal query:
        CustData.Grand Total > 0 AND Payments.Finalize BETWEEN [start] AND [end]

        Args:
            start_date: Start of pay period
            end_date: End of pay period

        Returns:
            List of Payment records with their associated tickets
        """
        from .ticket import Ticket

        return cls.query.join(Ticket).filter(
            Ticket.grand_total > 0,
            cls.finalized_at >= start_date,
            cls.finalized_at <= end_date,
            cls.status == 'Finalized'
        ).all()

    @classmethod
    def get_period_total(
        cls,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Get total revenue for a pay period.

        Args:
            start_date: Start of pay period
            end_date: End of pay period

        Returns:
            Total revenue amount
        """
        from sqlalchemy import func
        result = db.session.query(func.sum(cls.amount)).filter(
            cls.finalized_at >= start_date,
            cls.finalized_at <= end_date,
            cls.status == 'Finalized'
        ).scalar()
        return float(result) if result else 0.0
