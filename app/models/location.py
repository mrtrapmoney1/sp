"""
Location Model

Represents storage locations from the LOC.DBF and DISTINCTLOCATIONS tables.
Tracks storage locations with stock level indicators using 10% increment buckets.
"""

from datetime import datetime
from typing import Optional, List
from ..extensions import db


class Location(db.Model):
    """
    Location model representing a storage or work location.

    Maps to the LOC.APR and DISTINCTLOCATIONS.APR structures from the
    Lotus Approach system. Used for tracking where parts are stored
    and where service work is performed.
    """

    __tablename__ = 'locations'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Location identifiers
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

    # Location type
    location_type = db.Column(db.String(20), default='Storage')  # Storage, Workshop, Office, Vehicle

    # Address information (for service locations)
    address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(10))

    # Stock level indicator (10% increment buckets from DISTINCTLOCATIONS)
    # Values: 0-10%, 10-20%, 20-30%, ..., 90-100%
    stock_level_bucket = db.Column(db.String(10))

    # Active status
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Tags for organization (references LOCATION TAGS.APR)
    tags = db.Column(db.String(200))  # Comma-separated tags

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_items = db.relationship('Inventory', backref='location', lazy='dynamic')
    parts_history = db.relationship('PartsHistory', backref='location_ref', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Location {self.code}: {self.name}>'

    def update_stock_level(self) -> None:
        """
        Update the stock level bucket based on current inventory.

        Calculates the percentage of target stock currently on hand
        and assigns to appropriate 10% bucket.
        """
        total_target = sum(
            item.target_quantity or 0
            for item in self.inventory_items
        )
        total_on_hand = sum(
            item.quantity_on_hand or 0
            for item in self.inventory_items
        )

        if total_target == 0:
            self.stock_level_bucket = '0-10%'
            return

        percentage = (total_on_hand / total_target) * 100
        bucket_num = min(int(percentage // 10), 9)  # 0-9
        bucket_start = bucket_num * 10
        bucket_end = bucket_start + 10
        self.stock_level_bucket = f'{bucket_start}-{bucket_end}%'

    def get_inventory_summary(self) -> dict:
        """Get summary of inventory at this location."""
        items = list(self.inventory_items)
        total_value = sum(
            (item.quantity_on_hand or 0) * float(item.unit_cost or 0)
            for item in items
        )
        return {
            'total_items': len(items),
            'total_quantity': sum(item.quantity_on_hand or 0 for item in items),
            'total_value': total_value,
            'stock_level': self.stock_level_bucket,
        }

    def to_dict(self) -> dict:
        """Convert location to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'location_type': self.location_type,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'stock_level_bucket': self.stock_level_bucket,
            'is_active': self.is_active,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_by_code(cls, code: str) -> Optional['Location']:
        """Get location by code."""
        return cls.query.filter_by(code=code).first()

    @classmethod
    def get_active_locations(cls) -> List['Location']:
        """Get all active locations."""
        return cls.query.filter_by(is_active=True).order_by(cls.name).all()

    @classmethod
    def get_by_stock_level(cls, level: str) -> List['Location']:
        """
        Get locations by stock level bucket.

        Args:
            level: Stock level bucket (e.g., '0-10%', '50-60%')

        Returns:
            List of locations with matching stock level
        """
        return cls.query.filter_by(
            stock_level_bucket=level,
            is_active=True
        ).all()
