"""
Parts Analytics Service

Provides analytics and recommendations for parts based on historical
data. Uses SQLAlchemy for database queries and supports aggregation
across multiple part columns (P1-P11 pattern) using UNION queries.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, union_all, literal, case
from sqlalchemy.orm import Query

from ..extensions import db
from ..models import Ticket, PartsHistory

logger = logging.getLogger(__name__)


class PartsAnalyticsService:
    """
    Service for parts analytics and recommendations.

    Provides methods for analyzing parts usage patterns, generating
    recommendations based on historical data, and calculating
    confidence levels based on sample size.
    """

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 20
    MEDIUM_CONFIDENCE_THRESHOLD = 5

    def get_parts_history(
        self,
        search_term: str = None,
        limit: int = 500
    ) -> Tuple[List[Dict], int]:
        """
        Get parts history records with optional search filtering.

        Args:
            search_term: Optional search term to filter results
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of parts records, total count)
        """
        query = PartsHistory.query

        if search_term:
            search = f'%{search_term.lower()}%'
            query = query.filter(
                db.or_(
                    func.lower(PartsHistory.part_num).like(search),
                    func.lower(PartsHistory.part_descr).like(search),
                    func.lower(PartsHistory.vendor).like(search),
                    func.lower(PartsHistory.location).like(search),
                    PartsHistory.invoice.like(search),
                )
            )

        total = query.count()
        records = query.order_by(PartsHistory.created_at.desc()).limit(limit).all()

        return [r.to_dict() for r in records], total

    def get_parts_analytics(
        self,
        make: str = None,
        model: str = None,
        problem: str = None
    ) -> Dict:
        """
        Get analytics on parts usage with optional filtering.

        Args:
            make: Filter by appliance make
            model: Filter by appliance model
            problem: Filter by problem description

        Returns:
            Dictionary with analytics data including most common parts,
            common problems, and filtered statistics
        """
        # Build base query for tickets
        query = Ticket.query

        if make:
            query = query.filter(func.upper(Ticket.make).like(f'%{make.upper()}%'))
        if model:
            query = query.filter(func.upper(Ticket.model).like(f'%{model.upper()}%'))
        if problem:
            query = query.filter(func.lower(Ticket.service_req).like(f'%{problem.lower()}%'))

        filtered_tickets = query.all()
        total_tickets = Ticket.query.count()

        # Aggregate parts from P1-P11 columns
        all_parts = self._aggregate_ticket_parts(filtered_tickets)

        # Count part frequencies
        part_counts = {}
        for part in all_parts:
            part_num = part['part_number']
            if part_num not in part_counts:
                part_counts[part_num] = {
                    'part': part_num,
                    'description': part['description'],
                    'count': 0,
                    'total_quantity': 0,
                }
            part_counts[part_num]['count'] += 1
            part_counts[part_num]['total_quantity'] += part['quantity']

        # Sort by count
        most_common_parts = sorted(
            part_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        # Get common problems from filtered tickets
        problem_counts = {}
        for ticket in filtered_tickets:
            if ticket.service_req:
                prob = ticket.service_req[:100]  # Truncate for grouping
                problem_counts[prob] = problem_counts.get(prob, 0) + 1

        common_problems = sorted(
            [{'problem': p, 'count': c} for p, c in problem_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]

        # Get unique makes and models
        unique_makes = db.session.query(func.count(func.distinct(Ticket.make))).scalar() or 0
        unique_models = db.session.query(func.count(func.distinct(Ticket.model))).scalar() or 0

        return {
            'total_records': total_tickets,
            'filtered_records': len(filtered_tickets),
            'most_common_parts': most_common_parts,
            'common_problems': common_problems,
            'unique_makes': unique_makes,
            'unique_models': unique_models,
        }

    def get_recommendations(
        self,
        make: str = None,
        model: str = None,
        product_type: str = None,
        problem: str = None
    ) -> Dict:
        """
        Get part recommendations based on historical patterns.

        Uses multi-level filtering to find similar service cases and
        identifies most frequently used parts. Provides confidence
        levels based on sample size.

        Args:
            make: Appliance make
            model: Appliance model
            product_type: Product type (dw, ref, washer, etc.)
            problem: Problem description

        Returns:
            Dictionary with recommendations, confidence level, and
            details about filters applied
        """
        # Build filtered query
        query = Ticket.query
        filters_applied = []

        if make:
            query = query.filter(func.upper(Ticket.make).like(f'%{make.upper()}%'))
            filters_applied.append('make')
        if model:
            query = query.filter(func.upper(Ticket.model).like(f'%{model.upper()}%'))
            filters_applied.append('model')
        if product_type:
            query = query.filter(func.upper(Ticket.typ).like(f'%{product_type.upper()}%'))
            filters_applied.append('product_type')
        if problem:
            query = query.filter(func.lower(Ticket.service_req).like(f'%{problem.lower()}%'))
            filters_applied.append('problem')

        matching_tickets = query.all()
        total_matches = len(matching_tickets)

        if total_matches == 0:
            return {
                'recommendations': [],
                'confidence': 'none',
                'message': 'No matching records found. Try broader search criteria.',
                'filters_applied': filters_applied,
                'total_matches': 0,
            }

        # Aggregate parts with descriptions
        all_parts = self._aggregate_ticket_parts(matching_tickets)

        if not all_parts:
            return {
                'recommendations': [],
                'confidence': 'low',
                'message': 'Matching tickets found but no parts recorded.',
                'filters_applied': filters_applied,
                'total_matches': total_matches,
            }

        # Count part frequencies
        part_stats = {}
        for part in all_parts:
            key = (part['part_number'], part['description'])
            if key not in part_stats:
                part_stats[key] = 0
            part_stats[key] += 1

        # Sort and build recommendations
        sorted_parts = sorted(part_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        recommendations = []
        for (part_num, description), frequency in sorted_parts:
            success_rate = (frequency / total_matches) * 100
            recommendations.append({
                'part_number': part_num,
                'description': description,
                'frequency': frequency,
                'success_rate': f'{success_rate:.1f}%',
                'sample_size': total_matches,
            })

        # Determine confidence level
        if total_matches >= self.HIGH_CONFIDENCE_THRESHOLD:
            confidence = 'high'
        elif total_matches >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            confidence = 'medium'
        else:
            confidence = 'low'

        return {
            'recommendations': recommendations,
            'confidence': confidence,
            'filters_applied': filters_applied,
            'total_matches': total_matches,
        }

    def _aggregate_ticket_parts(self, tickets: List[Ticket]) -> List[Dict]:
        """
        Aggregate parts from P1-P11 columns across all tickets.

        Args:
            tickets: List of Ticket model instances

        Returns:
            List of dictionaries with part_number, description, quantity
        """
        all_parts = []

        for ticket in tickets:
            for i in range(1, 12):
                part_num = getattr(ticket, f'p{i}', None)
                if part_num and str(part_num).strip():
                    all_parts.append({
                        'part_number': str(part_num).strip(),
                        'description': str(getattr(ticket, f'pd{i}', '') or '').strip(),
                        'quantity': int(getattr(ticket, f'q{i}', 0) or 0),
                        'cost': float(getattr(ticket, f'c{i}', 0) or 0),
                    })

        return all_parts

    def get_parts_union_query(self) -> Query:
        """
        Create a UNION ALL query to aggregate parts across P1-P11 columns.

        This provides efficient aggregation without loading all ticket
        data into memory.

        Returns:
            SQLAlchemy query object for parts aggregation
        """
        # Build UNION of P1-P11 columns
        part_queries = []

        for i in range(1, 12):
            part_col = getattr(Ticket, f'p{i}')
            desc_col = getattr(Ticket, f'pd{i}')
            qty_col = getattr(Ticket, f'q{i}')
            cost_col = getattr(Ticket, f'c{i}')

            subq = db.session.query(
                Ticket.id.label('ticket_id'),
                Ticket.invoice.label('invoice'),
                Ticket.make.label('make'),
                Ticket.model.label('model'),
                Ticket.service_req.label('service_req'),
                part_col.label('part_num'),
                desc_col.label('part_desc'),
                qty_col.label('quantity'),
                cost_col.label('cost'),
                literal(i).label('slot_number'),
            ).filter(part_col.isnot(None), part_col != '')

            part_queries.append(subq)

        # Combine with UNION ALL
        return union_all(*part_queries)

    def get_customer_analytics(self) -> Dict:
        """
        Get analytics on customer database.

        Returns:
            Dictionary with customer statistics including top cities,
            top makes, and top product types
        """
        total_tickets = Ticket.query.count()

        # Top cities
        city_counts = db.session.query(
            Ticket.city,
            func.count(Ticket.id).label('count')
        ).filter(
            Ticket.city.isnot(None),
            Ticket.city != ''
        ).group_by(Ticket.city).order_by(func.count(Ticket.id).desc()).limit(10).all()

        top_cities = [
            {'city': city, 'count': count}
            for city, count in city_counts
            if city and city.lower() != 'nan'
        ]

        # Top makes
        make_counts = db.session.query(
            Ticket.make,
            func.count(Ticket.id).label('count')
        ).filter(
            Ticket.make.isnot(None),
            Ticket.make != ''
        ).group_by(Ticket.make).order_by(func.count(Ticket.id).desc()).limit(10).all()

        top_makes = [
            {'make': make, 'count': count}
            for make, count in make_counts
            if make and make.lower() != 'nan'
        ]

        # Top product types
        type_counts = db.session.query(
            Ticket.typ,
            func.count(Ticket.id).label('count')
        ).filter(
            Ticket.typ.isnot(None),
            Ticket.typ != ''
        ).group_by(Ticket.typ).order_by(func.count(Ticket.id).desc()).limit(10).all()

        top_types = [
            {'type': typ, 'count': count}
            for typ, count in type_counts
            if typ and typ.lower() != 'nan'
        ]

        # Unique counts
        unique_cities = db.session.query(func.count(func.distinct(Ticket.city))).scalar() or 0
        unique_zips = db.session.query(func.count(func.distinct(Ticket.zip))).scalar() or 0

        return {
            'total_customers': total_tickets,
            'unique_cities': unique_cities,
            'unique_zips': unique_zips,
            'top_cities': top_cities,
            'top_makes': top_makes,
            'top_product_types': top_types,
        }
