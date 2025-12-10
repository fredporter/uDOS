"""
uDOS v1.2.22 - Inbox Processing Handler

Processes files placed in memory/inbox/:
- CSV business location data (scraped listings)
- Automatic filtering, geocoding, and formatting
- Outputs to memory/bank/private/ or memory/shared/

Features:
- Email-only filtering (retains only records with email)
- Location parsing from FullAddress
- TILE code generation from lat/long
- Social media link extraction
- Keyword tagging from filename
"""

from pathlib import Path
from typing import Dict, List, Optional
import csv
import re
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
        """Process CSV file(s) in inbox."""
        if filename:
            file_path = self.inbox_path / filename
            if not file_path.exists():
                return f"❌ File not found: {filename}"
            files = [file_path]
        else:
            files = list(self.inbox_path.glob("*.csv"))
        
        if not files:
            return "📥 No CSV files to process in inbox"
        
        results = []
        for file_path in files:
            result = self._process_csv_file(file_path)
            results.append(result)
        
        return "\n\n".join(results)
    
    def _process_csv_file(self, file_path: Path) -> str:
        """Process a single CSV file."""
        keyword = self._extract_keyword(file_path.name)
        
        # Read CSV
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            return f"❌ Error reading {file_path.name}: {e}"
        
        # Filter and process
        processed_rows = []
        skipped = 0
        
        for row in rows:
            # Filter: Must have email
            if not row.get('Email') or row['Email'].strip() == '':
                skipped += 1
                continue
            
            # Process row
            processed = self._process_business_row(row, keyword)
            if processed:
                processed_rows.append(processed)
        
        # Save processed data
        if processed_rows:
            output_file = self.output_path / f"processed_{keyword}_{file_path.stem}.csv"
            self._save_processed_csv(output_file, processed_rows)
            
            return (f"✅ Processed: {file_path.name}\n"
                   f"   Keyword: {keyword}\n"
                   f"   Total Rows: {len(rows)}\n"
                   f"   With Email: {len(processed_rows)}\n"
                   f"   Skipped: {skipped}\n"
                   f"   Output: {output_file}")
        else:
            return f"⚠️  {file_path.name}: No rows with email addresses"
    
    def _process_business_row(self, row: Dict, keyword: str) -> Optional[Dict]:
        """Process a single business row."""
        # Extract location from FullAddress
        location_data = self._parse_address(row.get('FullAddress', ''))
        
        # Generate TILE code from lat/long
        lat = row.get('Lat', '')
        lng = row.get('Long', '')
        tile_code = self._latlong_to_tile(lat, lng) if lat and lng else ''
        
        # Extract clean data
        processed = {
            'Business_Name': row.get('Name', '').strip(),
            'Email': row.get('Email', '').strip(),
            'Phone': row.get('Phone', '').strip(),
            'Website': row.get('Website', '').strip(),
            'Keyword': keyword,
            'Street': location_data.get('street', ''),
            'Suburb': location_data.get('suburb', ''),
            'Postcode': location_data.get('postcode', ''),
            'Country': location_data.get('country', 'Australia'),
            'Lat': lat,
            'Long': lng,
            'TILE_Code': tile_code,
            'Facebook': row.get('Facebook', '').strip(),
            'Instagram': row.get('Instagram', '').strip(),
            'LinkedIn': row.get('LinkedIn', '').strip(),
            'Rating': row.get('Rating', ''),
            'Reviews': row.get('Reviews', ''),
        }
        
        return processed
    
    def _extract_keyword(self, filename: str) -> str:
        """Extract keyword from filename (e.g., 'pilates-studio' from 'example-pilates studio-Sutherland.csv')."""
        # Remove 'example-' prefix and file extension
        name = filename.replace('example-', '').replace('.csv', '')
        
        # Extract keyword (before location)
        parts = name.split('-')
        if len(parts) > 1:
            # Take first meaningful part (skip 'example')
            keyword = parts[0].strip().lower().replace(' ', '-')
        else:
            keyword = name.strip().lower().replace(' ', '-')
        
        return keyword
    
    def _parse_address(self, full_address: str) -> Dict[str, str]:
        """Parse FullAddress into components."""
        if not full_address:
            return {'street': '', 'suburb': '', 'postcode': '', 'country': ''}
        
        # Common patterns:
        # "Street Address, Suburb State Postcode Country"
        # "Street Address, Suburb State Postcode"
        # "Street Address, Suburb NSW Australia Postcode"
        
        parts = [p.strip() for p in full_address.split(',')]
        
        result = {
            'street': '',
            'suburb': '',
            'postcode': '',
            'country': 'Australia'
        }
        
        if len(parts) >= 1:
            result['street'] = parts[0]
        
        if len(parts) >= 2:
            # Last part usually has suburb/state/postcode
            last_part = parts[-1]
            
            # Extract postcode (4 digits)
            postcode_match = re.search(r'\b(\d{4})\b', last_part)
            if postcode_match:
                result['postcode'] = postcode_match.group(1)
            
            # Extract suburb (word before state/postcode)
            suburb_match = re.search(r'^([A-Za-z\s\-]+)', last_part)
            if suburb_match:
                result['suburb'] = suburb_match.group(1).strip()
            
            # Extract country if present
            if 'Australia' in last_part:
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
        # - Layer 100: World layer (~83km per cell)
        
        # Map longitude (-180 to 180) to column (0-479)
        col_index = int((lng_f + 180) * 479 / 360)
        col_index = max(0, min(479, col_index))
        
        # Map latitude (90 to -90) to row (0-269) - note: 90 is top (row 0)
        row_index = int((90 - lat_f) * 269 / 180)
        row_index = max(0, min(269, row_index))
        
        # Convert column index to AA-RL format
        col_letters = self._index_to_column(col_index)
        
        # TILE code format: AA340-100 (column + row + layer)
        return f"{col_letters}{row_index}-100"
    
    def _index_to_column(self, index: int) -> str:
        """Convert column index (0-479) to AA-RL format."""
        # AA=0, AB=1, ... AZ=25, BA=26, ... RL=479
        first = index // 26
        second = index % 26
        
        first_char = chr(ord('A') + first)
        second_char = chr(ord('A') + second)
        
        return f"{first_char}{second_char}"
    
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
