"""
DBF Export Service

Provides functionality to export service call data to dBase IV format
for compatibility with the Lotus Approach legacy system. Maintains
the exact 21-field structure required by CUSTDATA.DBF.
"""

import io
import struct
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# DBF field definitions for Lotus import (matches CUSTDATA.DBF)
DBF_FIELDS = [
    ('INVOICE', 'N', 5, 0),
    ('LASTNAME', 'C', 25, 0),
    ('FIRSTNAME', 'C', 15, 0),
    ('ADDRESS', 'C', 25, 0),
    ('CITY', 'C', 30, 0),
    ('STATE', 'C', 2, 0),
    ('ZIP', 'C', 5, 0),
    ('PHONE', 'C', 12, 0),
    ('PHONE2', 'C', 12, 0),
    ('LOCATION', 'C', 15, 0),
    ('SERVICEREQ', 'C', 250, 0),
    ('MAKE', 'C', 15, 0),
    ('TYP', 'C', 15, 0),
    ('MODEL', 'C', 20, 0),
    ('SERIAL', 'C', 26, 0),
    ('DATEIN', 'D', 8, 0),
    ('DATEPUR', 'D', 8, 0),
    ('BTADDRESS', 'C', 30, 0),
    ('ACCESSOR', 'C', 150, 0),
    ('TICLOC', 'C', 25, 0),
    ('DLRINVOICE', 'C', 17, 0),
]

# Warranty accessor mapping
WARRANTY_ACCESSOR_MAP = {
    'IW': 'If less than $550 then no approval is needed',
    'SC': '$140',
}


class DBFExportService:
    """
    Service for exporting data to dBase IV format.

    Creates DBF files compatible with the Lotus Approach system,
    maintaining the exact field structure and data types.
    """

    def __init__(self, fields: List[Tuple] = None):
        """
        Initialize export service.

        Args:
            fields: Optional custom field definitions. Defaults to DBF_FIELDS.
        """
        self.fields = fields or DBF_FIELDS

    def map_servicepower_call(self, call: Dict, invoice: str) -> Dict:
        """
        Map ServicePower call data to Lotus DBF fields.

        Args:
            call: ServicePower call data dictionary
            invoice: Invoice number to assign

        Returns:
            Dictionary with Lotus field names and values
        """
        today = datetime.now().strftime('%Y%m%d')

        # Handle phone2 - if "0", make it empty
        phone2 = call.get('ConsumerInfo_Phone2', call.get('consumer_info', {}).get('phone2', ''))
        if phone2 == '0':
            phone2 = ''

        # Determine accessor based on warranty type
        warranty = call.get('WarrantyType', call.get('warranty_type', ''))
        accessor = WARRANTY_ACCESSOR_MAP.get(warranty, '')

        # Extract ZIP (first 5 chars if longer)
        zip_code = call.get('ConsumerInfo_Postcode', call.get('consumer_info', {}).get('zip', ''))
        if len(zip_code) > 5:
            zip_code = zip_code.split('-')[0][:5]

        # Get call number for reference fields
        call_number = call.get('CallNumber', call.get('call_number', ''))

        # Get problem description (handle API typo)
        problem_desc = call.get('ProbelmDesc', call.get('problem_desc', call.get('ProblemDesc', '')))

        # Get product info (handle API typo MobelNo)
        model = call.get('ProductInfo_MobelNo', call.get('ProductInfo_ModelNo', ''))
        if not model and 'product_info' in call:
            model = call['product_info'].get('model', '')

        # Handle install date
        install_date = call.get('ProductInfo_InstallDate', '')
        if not install_date and 'product_info' in call:
            install_date = call['product_info'].get('install_date', '')
        if install_date:
            install_date = install_date.replace('/', '')[:8]

        # Build consumer info from either flat or nested structure
        consumer = call.get('consumer_info', {})
        product = call.get('product_info', {})

        return {
            'INVOICE': invoice,
            'LASTNAME': self._truncate(
                call.get('ConsumerInfo_ConsumerLastName', consumer.get('lastname', '')),
                25
            ),
            'FIRSTNAME': self._truncate(
                call.get('ConsumerInfo_ConsumerFirstName', consumer.get('firstname', '')),
                15
            ),
            'ADDRESS': self._truncate(
                call.get('ConsumerInfo_ConsumerAddress1', consumer.get('address', '')),
                25
            ),
            'CITY': self._truncate(
                call.get('ConsumerInfo_PostcodeLevel3', consumer.get('city', '')),
                30
            ),
            'STATE': self._truncate(
                call.get('ConsumerInfo_PostcodeLevel1', consumer.get('state', '')),
                2
            ),
            'ZIP': self._truncate(zip_code, 5),
            'PHONE': self._truncate(
                call.get('ConsumerInfo_Phone1', consumer.get('phone1', '')),
                12
            ),
            'PHONE2': self._truncate(phone2, 12),
            'LOCATION': 'Service Call',
            'SERVICEREQ': self._truncate(problem_desc, 250),
            'MAKE': self._truncate(
                call.get('ProductInfo_SPBrandDesc', product.get('brand', '')),
                15
            ),
            'TYP': self._truncate(
                call.get('ProductInfo_SPProductDesc', product.get('product', '')),
                15
            ),
            'MODEL': self._truncate(model, 20),
            'SERIAL': self._truncate(
                call.get('ProductInfo_SerialNo', product.get('serial', '')),
                26
            ),
            'DATEIN': today,
            'DATEPUR': install_date,
            'BTADDRESS': self._truncate(call_number, 30),
            'ACCESSOR': self._truncate(accessor, 150),
            'TICLOC': self._truncate(f"{datetime.now().strftime('%m/%d')} Gail", 25),
            'DLRINVOICE': self._truncate(call_number, 17),
        }

    def _truncate(self, value: str, max_length: int) -> str:
        """Truncate string to maximum length."""
        if value is None:
            return ''
        return str(value)[:max_length]

    def create_dbf(self, records: List[Dict]) -> bytes:
        """
        Create a DBF file from records.

        Args:
            records: List of dictionaries with Lotus field names and values

        Returns:
            DBF file contents as bytes
        """
        if not records:
            logger.warning('No records to export')
            return b''

        # Calculate record length (1 byte for deletion flag + sum of field lengths)
        record_len = 1 + sum(f[2] for f in self.fields)
        header_len = 32 + (len(self.fields) * 32) + 1  # Header + field descriptors + terminator

        now = datetime.now()
        num_records = len(records)

        logger.info(f'Creating DBF with {num_records} records')

        # Build DBF file in memory
        buffer = io.BytesIO()

        # Write header
        buffer.write(struct.pack('B', 0x03))  # dBase III
        buffer.write(struct.pack('B', now.year - 1900))
        buffer.write(struct.pack('B', now.month))
        buffer.write(struct.pack('B', now.day))
        buffer.write(struct.pack('<I', num_records))
        buffer.write(struct.pack('<H', header_len))
        buffer.write(struct.pack('<H', record_len))
        buffer.write(bytes(20))  # Reserved bytes

        # Write field descriptors
        for field_name, field_type, field_len, decimals in self.fields:
            field_name_bytes = field_name.encode('ascii')[:11].ljust(11, b'\x00')
            buffer.write(field_name_bytes)
            buffer.write(field_type.encode('ascii'))
            buffer.write(bytes(4))  # Reserved
            buffer.write(struct.pack('B', field_len))
            buffer.write(struct.pack('B', decimals))
            buffer.write(bytes(14))  # Reserved

        # Write field descriptor terminator
        buffer.write(b'\x0D')

        # Write records
        for record in records:
            buffer.write(b' ')  # Deletion flag (space = not deleted)

            for field_name, field_type, field_len, decimals in self.fields:
                value = record.get(field_name, '')

                if field_type == 'C':  # Character
                    value_bytes = str(value).encode('ascii', errors='ignore')[:field_len]
                    buffer.write(value_bytes.ljust(field_len, b' '))
                elif field_type == 'N':  # Numeric
                    value_str = str(value).rjust(field_len, ' ')
                    buffer.write(value_str.encode('ascii'))
                elif field_type == 'D':  # Date (YYYYMMDD)
                    if value and len(str(value)) == 8:
                        buffer.write(str(value).encode('ascii'))
                    else:
                        buffer.write(b' ' * 8)

        # Write end-of-file marker
        buffer.write(b'\x1A')

        return buffer.getvalue()

    def export_calls(
        self,
        calls: List[Dict],
        invoice_start: int = None
    ) -> Tuple[bytes, str]:
        """
        Export ServicePower calls to DBF format.

        Args:
            calls: List of ServicePower call dictionaries
            invoice_start: Starting invoice number (auto-generates if None)

        Returns:
            Tuple of (DBF file bytes, filename)
        """
        if not calls:
            return b'', ''

        # Generate invoice numbers if not provided
        if invoice_start is None:
            # Use timestamp-based invoice numbers
            invoice_start = int(datetime.now().strftime('%y%m%d')) * 100

        # Map calls to Lotus format
        lotus_records = []
        for i, call in enumerate(calls):
            invoice = str(invoice_start + i)
            lotus_record = self.map_servicepower_call(call, invoice)
            lotus_records.append(lotus_record)

        # Create DBF file
        dbf_data = self.create_dbf(lotus_records)

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'lotus_tickets_{timestamp}.dbf'

        logger.info(f'Exported {len(lotus_records)} records to {filename}')

        return dbf_data, filename

    def export_tickets(self, tickets: List) -> Tuple[bytes, str]:
        """
        Export Ticket model instances to DBF format.

        Args:
            tickets: List of Ticket model instances

        Returns:
            Tuple of (DBF file bytes, filename)
        """
        records = []
        for ticket in tickets:
            # Handle install date
            datepur = ''
            if ticket.date_purchased:
                datepur = ticket.date_purchased.strftime('%Y%m%d')

            record = {
                'INVOICE': ticket.invoice or '',
                'LASTNAME': self._truncate(ticket.lastname or '', 25),
                'FIRSTNAME': self._truncate(ticket.firstname or '', 15),
                'ADDRESS': self._truncate(ticket.address or '', 25),
                'CITY': self._truncate(ticket.city or '', 30),
                'STATE': self._truncate(ticket.state or '', 2),
                'ZIP': self._truncate(ticket.zip or '', 5),
                'PHONE': self._truncate(ticket.phone or '', 12),
                'PHONE2': self._truncate(ticket.phone2 or '', 12),
                'LOCATION': self._truncate(ticket.location or 'Service Call', 15),
                'SERVICEREQ': self._truncate(ticket.service_req or '', 250),
                'MAKE': self._truncate(ticket.make or '', 15),
                'TYP': self._truncate(ticket.typ or '', 15),
                'MODEL': self._truncate(ticket.model or '', 20),
                'SERIAL': self._truncate(ticket.serial or '', 26),
                'DATEIN': ticket.date_in.strftime('%Y%m%d') if ticket.date_in else '',
                'DATEPUR': datepur,
                'BTADDRESS': self._truncate(ticket.sp_call_number or '', 30),
                'ACCESSOR': self._truncate(ticket.accessor or '', 150),
                'TICLOC': self._truncate(ticket.tic_loc or '', 25),
                'DLRINVOICE': self._truncate(ticket.dlr_invoice or '', 17),
            }
            records.append(record)

        dbf_data = self.create_dbf(records)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'lotus_tickets_{timestamp}.dbf'

        return dbf_data, filename
