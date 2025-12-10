"""
uDOS v1.2.22 - Inbox Processing Handler

Processes files placed in memory/inbox/:
- CSV business location data (scraped listings)
- Automatic filtering, geocoding, and formatting
- Outputs to memory/bank/private/ or memory/shared/
- Archives processed files to memory/inbox/.archive/

Features:
- Email-only filtering (retains only records with email)
- Location parsing from FullAddress
- uCODE-compliant TILE codes (layer 500, alphanumeric base-36)
- Format: [COLUMN][ROW]-[LAYER]-[OFFSET] (e.g., AA340-500-A1B2)
- Reversible geocoding (TILE → lat/long)
- Social media link extraction
- Keyword tagging from filename
- Daily file consolidation with record updates
"""

from pathlib import Path
from typing import Dict, List, Optional
import csv
import re
from datetime import datetime
from .base_handler import BaseCommandHandler


class InboxHandler(BaseCommandHandler):
    """Handler for inbox file processing."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inbox_path = Path("memory/inbox")
        self.output_path = Path("memory/bank/private/processed")
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def handle(self, command: str, params: List[str], grid=None) -> str:
        """Route inbox commands.
        
        command will be the action (PROCESS/LIST/STATUS/CLEAN)
        params will be additional parameters like filename
        """
        if not command:
            return self._handle_inbox_status()
        
        action = command.upper()
        
        if action == "PROCESS":
            filename = params[0] if params else None
            return self._process_files(filename)
        elif action == "LIST":
            return self._list_inbox_files()
        elif action == "STATUS":
            return self._handle_inbox_status()
        elif action == "CLEAN":
            return self._clean_inbox()
        else:
            return f"❌ Unknown INBOX action: {action}\nUsage: INBOX PROCESS [file] | INBOX LIST | INBOX STATUS | INBOX CLEAN"
    
    def _handle_inbox_status(self) -> str:
        """Show inbox status."""
        files = list(self.inbox_path.glob("*.csv"))
        
        output = ["📥 INBOX STATUS", "=" * 60, ""]
        output.append(f"Inbox Path: {self.inbox_path}")
        output.append(f"Output Path: {self.output_path}")
        output.append(f"Files Waiting: {len(files)}")
        output.append("")
        
        if files:
            output.append("Files in Inbox:")
            for f in files:
                size_kb = f.stat().st_size / 1024
                output.append(f"  • {f.name} ({size_kb:.1f} KB)")
        else:
            output.append("✅ Inbox is empty")
        
        output.append("")
        output.append("Commands:")
        output.append("  INBOX PROCESS [file]  - Process CSV file(s)")
        output.append("  INBOX LIST           - List inbox files")
        output.append("  INBOX CLEAN          - Archive processed files")
        
        return "\n".join(output)
    
    def _list_inbox_files(self) -> str:
        """List files in inbox."""
        files = list(self.inbox_path.glob("*.csv"))
        
        if not files:
            return "📥 Inbox is empty"
        
        output = ["📥 INBOX FILES", "=" * 60, ""]
        for i, f in enumerate(files, 1):
            size_kb = f.stat().st_size / 1024
            keyword = self._extract_keyword(f.name)
            output.append(f"{i}. {f.name}")
            output.append(f"   Size: {size_kb:.1f} KB | Keyword: {keyword}")
            output.append("")
        
        return "\n".join(output)
    
    def _process_files(self, filename: Optional[str] = None) -> str:
        """Process CSV file(s) in inbox - combines into daily output file."""
        if filename:
            file_path = self.inbox_path / filename
            if not file_path.exists():
                return f"❌ File not found: {filename}"
            files = [file_path]
        else:
            files = list(self.inbox_path.glob("*.csv"))
        
        if not files:
            return "📥 No CSV files to process in inbox"
        
        # Ensure .archive directory exists
        archive_path = self.inbox_path / ".archive"
        archive_path.mkdir(exist_ok=True)
        
        # Daily output file
        today = datetime.now().strftime("%Y-%m-%d")
        daily_output = self.output_path / f"{today}-scraped-output.csv"
        
        # Load existing records if file exists (for deduplication)
        existing_records = {}
        if daily_output.exists():
            try:
                with open(daily_output, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        email = row.get('Email', '').strip().lower()
                        if email:
                            existing_records[email] = row
            except Exception:
                pass  # Start fresh if error reading
        
        # Process all files
        total_rows = 0
        total_processed = 0
        total_skipped = 0
        total_updated = 0
        processed_files = []
        
        for file_path in files:
            keyword = self._extract_keyword(file_path.name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    total_rows += len(rows)
                    
                    # Fill missing location data from adjacent rows
                    rows = self._fill_missing_locations(rows)
                    
                    for row in rows:
                        # Clean and validate email
                        email = self._clean_email(row.get('Email', ''))
                        if not email:
                            total_skipped += 1
                            continue
                        
                        # Process row
                        processed = self._process_business_row(row, keyword)
                        if processed:
                            email_key = email.lower()
                            if email_key in existing_records:
                                # Update existing record (merge non-empty values)
                                for k, v in processed.items():
                                    if v and (not existing_records[email_key].get(k) or v != existing_records[email_key].get(k)):
                                        existing_records[email_key][k] = v
                                total_updated += 1
                            else:
                                existing_records[email_key] = processed
                                total_processed += 1
                        else:
                            total_skipped += 1
            
            except Exception as e:
                return f"❌ Error processing {file_path.name}: {e}"
            
            # Mark file for archiving after successful processing
            processed_files.append(file_path)
        
        # Save combined daily output
        if existing_records:
            # Fill missing location data from adjacent records
            filled_records = self._fill_missing_location_fields(list(existing_records.values()))
            self._save_processed_csv(daily_output, filled_records)
            
            # Move processed files to .archive/
            archived_count = 0
            for file_path in processed_files:
                try:
                    archive_dest = archive_path / file_path.name
                    # If file exists in archive, append timestamp
                    if archive_dest.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        archive_dest = archive_path / f"{timestamp}_{file_path.name}"
                    file_path.rename(archive_dest)
                    archived_count += 1
                except Exception as e:
                    # Continue if archiving fails
                    pass
            
            return (f"✅ Processed {len(files)} file(s)\n"
                   f"   Total Rows: {total_rows}\n"
                   f"   New Records: {total_processed}\n"
                   f"   Updated Records: {total_updated}\n"
                   f"   Skipped (no email): {total_skipped}\n"
                   f"   Output: {daily_output}\n"
                   f"   Total Unique Records: {len(existing_records)}\n"
                   f"   Archived Files: {archived_count}/{len(files)}")
        else:
            return f"⚠️  No valid records with email addresses"
    
    def _fill_missing_locations(self, rows: List[Dict]) -> List[Dict]:
        """Fill missing FullAddress from adjacent rows in the same sheet."""
        for i, row in enumerate(rows):
            # If FullAddress is missing or empty
            if not row.get('FullAddress', '').strip():
                # Try to copy from previous row
                if i > 0 and rows[i-1].get('FullAddress', '').strip():
                    row['FullAddress'] = rows[i-1]['FullAddress']
                # If still empty, try next row
                elif i < len(rows) - 1 and rows[i+1].get('FullAddress', '').strip():
                    row['FullAddress'] = rows[i+1]['FullAddress']
        
        return rows
    
    def _fill_missing_location_fields(self, rows: List[Dict]) -> List[Dict]:
        """Fill missing Street/Suburb/State/Postcode/Country from adjacent rows in final output."""
        location_fields = ['Street', 'Suburb', 'State', 'Postcode', 'Country']
        
        for i, row in enumerate(rows):
            for field in location_fields:
                # If field is missing or empty
                if not row.get(field, '').strip():
                    # Try to copy from previous row
                    if i > 0 and rows[i-1].get(field, '').strip():
                        row[field] = rows[i-1][field]
                    # If still empty, try next row
                    elif i < len(rows) - 1 and rows[i+1].get(field, '').strip():
                        row[field] = rows[i+1][field]
        
        return rows
    
    def _clean_email(self, email: str) -> str:
        """Clean and validate email address."""
        if not email:
            return ''
        
        # Remove mailto: prefix
        email = email.replace('mailto:', '').strip()
        
        # Basic email validation (has @ and .)
        if '@' not in email or '.' not in email:
            return ''
        
        # Remove invalid/placeholder emails
        invalid_patterns = [
            'sentry-next.wixpress.com',
            'example.com',
            'test.com',
            '@facebook.com',
            'fbml'
        ]
        
        email_lower = email.lower()
        for pattern in invalid_patterns:
            if pattern in email_lower:
                return ''
        
        return email
    
    def _format_phone(self, phone: str) -> str:
        """Format phone to international format (+61...)."""
        if not phone:
            return ''
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        if not digits:
            return ''
        
        # Australian numbers
        if digits.startswith('61'):
            # Already has country code
            return f"+{digits}"
        elif digits.startswith('0'):
            # Remove leading 0, add +61
            return f"+61{digits[1:]}"
        elif len(digits) == 9:
            # Missing leading 0, add +61
            return f"+61{digits}"
        elif len(digits) >= 10:
            # Standard AU format
            return f"+61{digits}" if not digits.startswith('61') else f"+{digits}"
        
        # Return original if can't parse
        return phone
    
    def _clean_business_name(self, name: str) -> str:
        """Clean and format business name with relaxed title case."""
        if not name:
            return ''
        
        name = name.strip()
        
        # Convert & to 'and'
        name = name.replace('&', 'and')
        
        # Remove special characters (keep letters, numbers, spaces, hyphens)
        name = re.sub(r'[^\w\s\-]', '', name)
        
        # Clean up extra whitespace
        name = ' '.join(name.split())
        
        # Relaxed title case - keep common words lowercase
        lowercase_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = name.split()
        formatted_words = []
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Always capitalize first word
            if i == 0:
                # Keep acronyms (2-3 uppercase letters) as-is
                if len(word) <= 3 and word.isupper():
                    formatted_words.append(word)
                else:
                    formatted_words.append(word.title())
            # Keep common words lowercase (unless they're acronyms)
            elif word_lower in lowercase_words:
                formatted_words.append(word_lower)
            # Keep acronyms (2-3 uppercase letters) as-is
            elif len(word) <= 3 and word.isupper():
                formatted_words.append(word)
            # Otherwise apply title case
            else:
                formatted_words.append(word.title())
        
        return ' '.join(formatted_words)
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing query parameters and fragments, filter invalid URLs."""
        if not url:
            return ''
        
        url = url.strip()
        
        # Filter out invalid/tracking URLs
        invalid_patterns = [
            '/tr?',           # Facebook tracking pixels
            '/fbml',          # Old Facebook markup language URLs
            '/2008/',         # Old broken Facebook URLs
            'wix_google',     # Wix tracking
        ]
        
        for pattern in invalid_patterns:
            if pattern in url:
                return ''
        
        # Remove query parameters (?key=value&...)
        if '?' in url:
            url = url.split('?')[0]
        
        # Remove fragments (#section)
        if '#' in url:
            url = url.split('#')[0]
        
        return url
    
    def _process_business_row(self, row: Dict, keyword: str) -> Optional[Dict]:
        """Process a single business row."""
        # Clean email
        email = self._clean_email(row.get('Email', ''))
        if not email:
            return None
        
        # Extract location from FullAddress
        location_data = self._parse_address(row.get('FullAddress', ''))
        
        # Generate TILE code from lat/long
        lat = row.get('Lat', '')
        lng = row.get('Long', '')
        tile_code = self._latlong_to_tile(lat, lng) if lat and lng else ''
        
        # Format phone number
        phone = self._format_phone(row.get('Phone', ''))
        
        # Clean URLs
        website = self._clean_url(row.get('Website', ''))
        facebook = self._clean_url(row.get('Facebook', ''))
        instagram = self._clean_url(row.get('Instagram', ''))
        linkedin = self._clean_url(row.get('LinkedIn', ''))
        
        # Clean business name
        business_name = self._clean_business_name(row.get('Name', ''))
        
        # Extract clean data
        processed = {
            'Business_Name': business_name,
            'Email': email,
            'Phone': phone,
            'Website': website,
            'Keyword': keyword,
            'Street': location_data.get('street', ''),
            'Suburb': location_data.get('suburb', ''),
            'State': location_data.get('state', ''),
            'Postcode': location_data.get('postcode', ''),
            'Country': location_data.get('country', 'Australia'),
            'TILE_Code': tile_code,
            'Facebook': facebook,
            'Instagram': instagram,
            'LinkedIn': linkedin,
            'Rating': row.get('Rating', ''),
            'Reviews': row.get('Reviews', ''),
        }
        
        return processed
    
    def _extract_keyword(self, filename: str) -> str:
        """Extract keyword from filename.
        
        Examples:
            '1Google-Quick-ndis-Melbourne Victoria Australia.csv' → 'ndis'
            'example-pilates studio-Sutherland Shire NSW.csv' → 'pilates-studio'
            '20251210_205418_example-pilates studio-Sutherland.csv' → 'pilates-studio'
        """
        # Remove timestamp prefix if present (e.g., '20251210_205418_')
        import re
        name = re.sub(r'^\d{8}_\d{6}_', '', filename)
        
        # Remove file extension
        name = name.replace('.csv', '')
        
        # Remove common prefixes
        name = name.replace('example-', '')
        
        # Split by dash and filter meaningful parts
        parts = [p.strip() for p in name.split('-') if p.strip()]
        
        # Filter out common non-keyword parts
        skip_words = {'google', 'quick', '1google', '2google', 'nsw', 'vic', 'qld', 'sa', 'wa', 'nt', 'tas', 'act',
                     'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'darwin', 'hobart', 'canberra'}
        
        # Find first meaningful keyword (not a prefix, location, or state)
        for part in parts:
            part_lower = part.lower().replace(' ', '-')
            # Skip single digits/letters and common prefixes
            if len(part_lower) > 1 and not part_lower.isdigit() and part_lower not in skip_words:
                return part_lower
        
        # Fallback: use first part
        return parts[0].lower().replace(' ', '-') if parts else 'unknown'
    
    def _parse_address(self, full_address: str) -> Dict[str, str]:
        """Parse FullAddress into components with proper State separation."""
        if not full_address:
            return {'street': '', 'suburb': '', 'state': '', 'postcode': '', 'country': ''}
        
        # Common patterns:
        # "Street Address, Suburb State Postcode, Country"
        # "Street Address, Suburb NSW 2234, Australia"
        
        parts = [p.strip() for p in full_address.split(',')]
        
        result = {
            'street': '',
            'suburb': '',
            'state': '',
            'postcode': '',
            'country': 'Australia'
        }
        
        if len(parts) >= 1:
            result['street'] = parts[0]
        
        if len(parts) >= 2:
            # Second part usually has suburb/state/postcode
            middle_part = parts[1]
            
            # Extract state (NSW, VIC, QLD, etc.)
            state_match = re.search(r'\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b', middle_part)
            if state_match:
                result['state'] = state_match.group(1)
            
            # Extract postcode (4 digits)
            postcode_match = re.search(r'\b(\d{4})\b', middle_part)
            if postcode_match:
                result['postcode'] = postcode_match.group(1)
            
            # Extract suburb (text before state)
            if result['state']:
                suburb_match = re.match(r'^([A-Za-z\s\-]+)', middle_part)
                if suburb_match:
                    suburb = suburb_match.group(1).strip()
                    # Remove state abbreviation if it got included
                    suburb = re.sub(r'\b(NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\b', '', suburb).strip()
                    result['suburb'] = suburb
        
        # Check for country in last part
        if len(parts) >= 3:
            if 'Australia' in parts[-1]:
                result['country'] = 'Australia'
        
        return result
    
    def _latlong_to_tile(self, lat: str, lng: str) -> str:
        """Convert lat/long to TILE code (uDOS grid system)."""
        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (ValueError, TypeError):
            return ''
        
        # uDOS grid specs:
        # - Columns: AA-RL (0-479) covering longitude -180 to 180
        # - Rows: 0-269 covering latitude -90 to 90
        # - Layer 500: Block layer (~1.5m precision with 3-char base-36)
        # - Format: [COLUMN][ROW]-[LAYER]-[OFFSET] (alphanumeric only)
        
        # Map longitude (-180 to 180) to column (0-479)
        col_index = int((lng_f + 180) * 479 / 360)
        col_index = max(0, min(479, col_index))
        
        # Map latitude (90 to -90) to row (0-269) - note: 90 is top (row 0)
        row_index = int((90 - lat_f) * 269 / 180)
        row_index = max(0, min(269, row_index))
        
        # Convert column index to AA-RL format
        col_letters = self._index_to_column(col_index)
        
        # For layer 500 (block level), encode sub-cell precision in base-36
        # Calculate offset within cell (0-46655 = 36^3-1 for each axis)
        lng_offset = int(((lng_f + 180) * 479 / 360 - col_index) * 46656) % 46656
        lat_offset = int((((90 - lat_f) * 269 / 180) - row_index) * 46656) % 46656
        
        # Convert to base-36 (0-9, A-Z): 3 chars each = 6 char total
        lng_b36 = self._to_base36(lng_offset, 3)
        lat_b36 = self._to_base36(lat_offset, 3)
        
        # TILE code format: AA340-500-A1B2C3 (alphanumeric with dashes only)
        return f"{col_letters}{row_index}-500-{lng_b36}{lat_b36}"
    
    def _index_to_column(self, index: int) -> str:
        """Convert column index (0-479) to AA-RL format."""
        # AA=0, AB=1, ... AZ=25, BA=26, ... RL=479
        first = index // 26
        second = index % 26
        
        first_char = chr(ord('A') + first)
        second_char = chr(ord('A') + second)
        
        return f"{first_char}{second_char}"
    
    def _to_base36(self, num: int, width: int) -> str:
        """Convert number to base-36 (0-9, A-Z) with fixed width."""
        if num < 0 or num >= 36**width:
            num = 0
        
        digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''
        
        for _ in range(width):
            result = digits[num % 36] + result
            num //= 36
        
        return result
    
    @staticmethod
    def tile_to_latlong(tile_code: str) -> tuple:
        """Convert TILE code back to lat/long coordinates.
        
        Args:
            tile_code: TILE format AA340-500-A1B2C3 (alphanumeric base-36, 3 chars per axis)
            
        Returns:
            Tuple of (latitude, longitude) as floats
        """
        # Parse: QY185-500-A1B2C3
        parts = tile_code.split('-')
        col_row = parts[0]
        layer = parts[1] if len(parts) > 1 else '500'
        offset_str = parts[2] if len(parts) > 2 else '000000'
        
        # Extract column letters and row number
        col_letters = col_row[:2]
        row_num = int(col_row[2:])
        
        # Decode base-36 offsets (6 chars: 3 for lng, 3 for lat)
        def from_base36(s: str) -> int:
            digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            result = 0
            for char in s:
                result = result * 36 + digits.index(char.upper())
            return result
        
        if len(offset_str) >= 6:
            lng_offset = from_base36(offset_str[:3])
            lat_offset = from_base36(offset_str[3:6])
        else:
            lng_offset, lat_offset = 0, 0
        
        # Convert column letters to index (AA=0, AB=1, ...)
        first_char = ord(col_letters[0]) - ord('A')
        second_char = ord(col_letters[1]) - ord('A')
        col_index = first_char * 26 + second_char
        
        # Map back to coordinates (36^3 = 46656 divisions per cell)
        lng = (col_index + lng_offset/46656) * 360 / 479 - 180
        lat = 90 - (row_num + lat_offset/46656) * 180 / 269
        
        return round(lat, 6), round(lng, 6)
    
    def _save_processed_csv(self, output_file: Path, rows: List[Dict]) -> None:
        """Save processed data to CSV."""
        if not rows:
            return
        
        fieldnames = list(rows[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def _clean_inbox(self) -> str:
        """Archive processed files from inbox."""
        archive_path = self.inbox_path / ".archive"
        archive_path.mkdir(exist_ok=True)
        
        files = list(self.inbox_path.glob("*.csv"))
        if not files:
            return "📥 Inbox is already empty"
        
        moved = 0
        for file_path in files:
            # Move to archive
            dest = archive_path / file_path.name
            file_path.rename(dest)
            moved += 1
        
        return f"✅ Archived {moved} file(s) to {archive_path}"
