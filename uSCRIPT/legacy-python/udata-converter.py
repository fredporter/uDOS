#!/usr/bin/env python3
"""
uDATA Parser and Converter v1.0
Pure Python implementation for converting JSON to uDATA format
Generates minified JSON with line breaks per record
"""

import json
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any, Union

class uDATAParser:
    """
    uDATA format parser and converter

    uDATA Format:
    - Minified JSON records, one per line
    - No spaces in JSON (compact format)
    - Line breaks separate records
    - Optional metadata record
    """

    @staticmethod
    def parse_file(file_path: str) -> List[Dict[str, Any]]:
        """Parse uDATA format file (JSON records, one per line)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return uDATAParser.parse_content(f.read())
        except Exception as e:
            print(f"❌ Error reading uDATA file {file_path}: {e}")
            return []

    @staticmethod
    def parse_content(content: str) -> List[Dict[str, Any]]:
        """Parse uDATA format content string"""
        records = []
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        for line_num, line in enumerate(lines, 1):
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing uDATA line {line_num}: {e}")
                print(f"   Line content: {line}")

        return records

    @staticmethod
    def to_udata(records: List[Dict[str, Any]],
                 minified: bool = True,
                 sort_keys: bool = False,
                 add_metadata: bool = False) -> str:
        """Convert array of objects to uDATA format"""

        result_records = []

        # Add metadata record at the beginning if requested
        if add_metadata:
            metadata_record = {
                "metadata": {
                    "format": "uDATA",
                    "version": "1.0",
                    "generated": datetime.now().isoformat(),
                    "records": len(records),
                    "description": "uDOS Data Format - Minified JSON records, one per line"
                }
            }
            result_records.append(metadata_record)

        # Add all data records
        result_records.extend(records)

        # Convert to JSON lines
        lines = []
        for record in result_records:
            if sort_keys:
                # Sort the keys for consistent output
                json_str = json.dumps(record, sort_keys=True, separators=(',', ':') if minified else (',', ': '))
            else:
                json_str = json.dumps(record, separators=(',', ':') if minified else (',', ': '))
            lines.append(json_str)

        return '\n'.join(lines)

    @staticmethod
    def write_file(file_path: str,
                   records: List[Dict[str, Any]],
                   minified: bool = True,
                   add_metadata: bool = True,
                   sort_keys: bool = False) -> bool:
        """Write records to uDATA format file"""
        try:
            content = uDATAParser.to_udata(records, minified, sort_keys, add_metadata)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Wrote {len(records)} records to {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing uDATA file {file_path}: {e}")
            return False

    @staticmethod
    def convert_json_to_udata(input_path: str,
                              output_path: str,
                              add_metadata: bool = True,
                              preserve_structure: bool = False,
                              sort_keys: bool = False) -> bool:
        """Convert traditional JSON file to uDATA format"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            records = []

            if isinstance(json_data, list):
                # Already an array of records
                records = json_data
            elif isinstance(json_data, dict):
                # Handle object-based JSON

                # Preserve existing metadata separately if not preserving structure
                if 'metadata' in json_data and not preserve_structure:
                    records.append({"metadata": json_data['metadata']})
                    del json_data['metadata']

                # Convert remaining object properties to records
                for key, value in json_data.items():
                    if isinstance(value, list):
                        # Handle arrays - each item becomes a record
                        for index, item in enumerate(value):
                            if isinstance(item, dict):
                                record = {"category": key, "index": index}
                                record.update(item)
                                records.append(record)
                            else:
                                records.append({
                                    "category": key,
                                    "index": index,
                                    "value": item
                                })
                    elif isinstance(value, dict):
                        # Nested object becomes a record
                        record = {"name": key}
                        record.update(value)
                        records.append(record)
                    else:
                        # Simple value
                        records.append({"name": key, "value": value})

            return uDATAParser.write_file(output_path, records,
                                         minified=True,
                                         add_metadata=add_metadata,
                                         sort_keys=sort_keys)

        except Exception as e:
            print(f"❌ Error converting JSON to uDATA: {e}")
            return False

    @staticmethod
    def read_universal(file_path: str) -> List[Dict[str, Any]]:
        """Read and parse both JSON and uDATA formats automatically"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Check if it's uDATA format (multiple lines with JSON objects)
            lines = [line.strip() for line in content.split('\n') if line.strip()]

            if len(lines) > 1:
                # Likely uDATA format
                return uDATAParser.parse_content(content)
            else:
                # Likely regular JSON
                json_data = json.loads(content)

                if isinstance(json_data, list):
                    return json_data
                else:
                    # Convert single object to array
                    return [json_data]

        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return []

    @staticmethod
    def validate_file(file_path: str) -> bool:
        """Validate uDATA format file"""
        try:
            records = uDATAParser.parse_file(file_path)
            return len(records) > 0
        except Exception as e:
            print(f"❌ uDATA validation failed for {file_path}: {e}")
            return False

    @staticmethod
    def get_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about uDATA records"""
        stats = {
            "total_records": len(records),
            "metadata_records": 0,
            "data_records": 0,
            "unique_keys": set(),
            "categories": set(),
            "record_types": {}
        }

        for record in records:
            if "metadata" in record:
                stats["metadata_records"] += 1
            else:
                stats["data_records"] += 1

            # Collect all keys
            for key in record.keys():
                stats["unique_keys"].add(key)

            # Collect categories
            if "category" in record:
                stats["categories"].add(record["category"])

            # Count record types
            if "type" in record:
                record_type = record["type"]
                stats["record_types"][record_type] = stats["record_types"].get(record_type, 0) + 1

        # Convert sets to lists for JSON serialization
        stats["unique_keys"] = sorted(list(stats["unique_keys"]))
        stats["categories"] = sorted(list(stats["categories"]))

        return stats

    @staticmethod
    def show_info(file_path: str):
        """Show detailed information about uDATA file"""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        print(f"📊 uDATA File Information: {file_path}")
        print("=" * 50)

        # File stats
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"📁 File Size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
        print(f"📄 Total Lines: {len(lines):,}")

        # Parse and analyze records
        records = uDATAParser.parse_file(file_path)
        if not records:
            print("❌ No valid records found")
            return

        stats = uDATAParser.get_stats(records)

        print(f"📋 Total Records: {stats['total_records']:,}")
        print(f"🏷️  Metadata Records: {stats['metadata_records']:,}")
        print(f"💾 Data Records: {stats['data_records']:,}")
        print(f"🔑 Unique Keys: {len(stats['unique_keys'])}")
        print(f"📂 Categories: {len(stats['categories'])}")

        if stats['categories']:
            print(f"   Categories: {', '.join(stats['categories'])}")

        if stats['record_types']:
            print(f"🏗️  Record Types:")
            for record_type, count in stats['record_types'].items():
                print(f"   {record_type}: {count}")

        # Show sample records
        print(f"\n📋 Sample Records (first 3):")
        for i, record in enumerate(records[:3]):
            print(f"   {i+1}: {json.dumps(record, separators=(',', ':'))}")

        # Show metadata if available
        metadata_records = [r for r in records if "metadata" in r]
        if metadata_records:
            print(f"\n🏷️  Metadata:")
            for key, value in metadata_records[0]["metadata"].items():
                print(f"   {key}: {value}")

def main():
    parser = argparse.ArgumentParser(description='uDATA Parser and Converter v1.0')
    parser.add_argument('input', nargs='?', help='Input JSON file or command')
    parser.add_argument('output', nargs='?', help='Output uDATA file')
    parser.add_argument('--validate', action='store_true', help='Validate uDATA file')
    parser.add_argument('--info', action='store_true', help='Show file information')
    parser.add_argument('--no-metadata', action='store_true', help='Don\'t add metadata record')
    parser.add_argument('--sort-keys', action='store_true', help='Sort JSON keys')
    parser.add_argument('--preserve-structure', action='store_true', help='Preserve original JSON structure')

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return

    if args.validate:
        if uDATAParser.validate_file(args.input):
            print(f"✅ Valid uDATA file: {args.input}")
        else:
            print(f"❌ Invalid uDATA file: {args.input}")
            sys.exit(1)
    elif args.info:
        uDATAParser.show_info(args.input)
    else:
        # Convert JSON to uDATA
        if not os.path.exists(args.input):
            print(f"❌ Input file not found: {args.input}")
            sys.exit(1)

        output_file = args.output or args.input.replace('.json', '.udata')

        success = uDATAParser.convert_json_to_udata(
            args.input,
            output_file,
            add_metadata=not args.no_metadata,
            preserve_structure=args.preserve_structure,
            sort_keys=args.sort_keys
        )

        if success:
            print(f"✅ Conversion completed successfully!")
            uDATAParser.show_info(output_file)
        else:
            print(f"❌ Conversion failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
