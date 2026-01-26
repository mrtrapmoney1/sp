"""
Inventory Model

Represents inventory items from the STOCK ONLY.APR table.
Tracks current stock levels by location with automatic updates
when parts are used in service tickets.
"""

from datetime import datetime
from typing import Optional, List
from ..extensions import db


class Inventory(db.Model):
    """
    Inventory model representing stock items at a specific location.

    Maps to the STOCK ONLY.APR structure from the Lotus Approach system.
    Tracks part quantities, reorder points, and stock value by location.
    """

    __tablename__ = 'inventory'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Part identification
    part_num = db.Column(db.String(50), nullable=False, index=True)
    part_descr = db.Column(db.String(200))

    # Location (FK to locations table)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False, index=True)

    # Stock levels
    quantity_on_hand = db.Column(db.Integer, default=0)
    quantity_reserved = db.Column(db.Integer, default=0)  # Reserved for pending orders
    quantity_on_order = db.Column(db.Integer, default=0)

    # Reorder settings
    reorder_point = db.Column(db.Integer, default=0)
    target_quantity = db.Column(db.Integer, default=0)

    # Cost information
    unit_cost = db.Column(db.Numeric(10, 2))
    last_purchase_cost = db.Column(db.Numeric(10, 2))

    # Vendor information
    vendor = db.Column(db.String(50), default='Marcone')
    vendor_part_num = db.Column(db.String(50))

    # Status
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_core = db.Column(db.Boolean, default=False)  # Core exchange part
    is_obsolete = db.Column(db.Boolean, default=False)

    # Dates
    last_received = db.Column(db.Date)
    last_used = db.Column(db.Date)

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint for part/location combination
    __table_args__ = (
        db.UniqueConstraint('part_num', 'location_id', name='uq_inventory_part_location'),
    )

    def __repr__(self) -> str:
        return f'<Inventory {self.part_num} @ {self.location_id}: {self.quantity_on_hand}>'

    @property
    def quantity_available(self) -> int:
        """Get available quantity (on hand minus reserved)."""
        return (self.quantity_on_hand or 0) - (self.quantity_reserved or 0)

    @property
    def total_value(self) -> float:
        """Get total value of stock on hand."""
        return (self.quantity_on_hand or 0) * float(self.unit_cost or 0)

    @property
    def needs_reorder(self) -> bool:
        """Check if stock is at or below reorder point."""
        if not self.reorder_point:
            return False
        return self.quantity_available <= self.reorder_point

    def adjust_quantity(self, quantity: int, reason: str = None) -> None:
        """
        Adjust stock quantity.

        Args:
            quantity: Amount to add (positive) or remove (negative)
            reason: Optional reason for adjustment
        """
        self.quantity_on_hand = (self.quantity_on_hand or 0) + quantity
        if self.quantity_on_hand < 0:
            self.quantity_on_hand = 0
        self.updated_at = datetime.utcnow()

        if quantity < 0:
            self.last_used = datetime.utcnow().date()
        elif quantity > 0:
            self.last_received = datetime.utcnow().date()

    def reserve(self, quantity: int) -> bool:
        """
        Reserve stock for a pending order.

        Args:
            quantity: Amount to reserve

        Returns:
            True if reservation successful, False if insufficient stock
        """
        if quantity > self.quantity_available:
            return False
        self.quantity_reserved = (self.quantity_reserved or 0) + quantity
        return True

    def release_reservation(self, quantity: int) -> None:
        """
        Release reserved stock.

        Args:
            quantity: Amount to release from reservation
        """
        self.quantity_reserved = max(0, (self.quantity_reserved or 0) - quantity)

    def fulfill_reservation(self, quantity: int) -> None:
        """
        Fulfill a reservation by decrementing both reserved and on-hand.

        Args:
            quantity: Amount to fulfill
        """
        self.quantity_reserved = max(0, (self.quantity_reserved or 0) - quantity)
        self.quantity_on_hand = max(0, (self.quantity_on_hand or 0) - quantity)
        self.last_used = datetime.utcnow().date()

    def to_dict(self) -> dict:
        """Convert inventory to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'part_num': self.part_num,
            'part_descr': self.part_descr,
            'location_id': self.location_id,
            'quantity_on_hand': self.quantity_on_hand,
            'quantity_reserved': self.quantity_reserved,
            'quantity_available': self.quantity_available,
            'quantity_on_order': self.quantity_on_order,
            'reorder_point': self.reorder_point,
            'target_quantity': self.target_quantity,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_value': self.total_value,
            'vendor': self.vendor,
            'vendor_part_num': self.vendor_part_num,
            'is_active': self.is_active,
            'is_core': self.is_core,
            'is_obsolete': self.is_obsolete,
            'needs_reorder': self.needs_reorder,
            'last_received': self.last_received.isoformat() if self.last_received else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_part_location(cls, part_num: str, location_id: int) -> Optional['Inventory']:
        """Get inventory record by part number and location."""
        return cls.query.filter_by(
            part_num=part_num,
            location_id=location_id
        ).first()

    @classmethod
    def get_low_stock_items(cls) -> List['Inventory']:
        """Get all items at or below reorder point."""
        return cls.query.filter(
            cls.is_active == True,
            cls.reorder_point > 0,
            cls.quantity_on_hand <= cls.reorder_point
        ).all()

    @classmethod
    def get_by_part_all_locations(cls, part_num: str) -> List['Inventory']:
        """Get inventory for a part across all locations."""
        return cls.query.filter_by(
            part_num=part_num,
            is_active=True
        ).all()

    @classmethod
    def get_total_on_hand(cls, part_num: str) -> int:
        """Get total quantity on hand for a part across all locations."""
        from sqlalchemy import func
        result = db.session.query(func.sum(cls.quantity_on_hand)).filter(
            cls.part_num == part_num,
            cls.is_active == True
        ).scalar()
        return int(result) if result else 0
