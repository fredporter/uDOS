#!/usr/bin/env python3
"""
Convert formatted/pretty-printed JSON files with multiple objects to uDATA format
Handles JSON files that have multiple objects separated by whitespace/newlines
"""

import json
import sys
import re
from datetime import datetime

def extract_json_objects(text):
    """Extract individual JSON objects from text that may contain multiple objects"""
    objects = []
    current_obj = ""
    brace_count = 0
    in_string = False
    escaped = False

    for char in text:
        if escaped:
            escaped = False
            current_obj += char
            continue

        if char == '\\' and in_string:
            escaped = True
            current_obj += char
            continue

        if char == '"' and not escaped:
            in_string = not in_string

        current_obj += char

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Complete object found
                    try:
                        obj = json.loads(current_obj.strip())
                        objects.append(obj)
                        current_obj = ""
                    except json.JSONDecodeError:
                        pass

    return objects

def convert_formatted_to_udata(input_file, output_file):
    """Convert formatted JSON to uDATA format"""
    try:
        with open(input_file, 'r') as f:
            content = f.read()

        # Extract all JSON objects
        objects = extract_json_objects(content)

        if not objects:
            print(f"❌ No valid JSON objects found in {input_file}")
            return False

        # Add metadata if first object isn't metadata
        records_to_write = []
        if not objects or not isinstance(objects[0], dict) or 'metadata' not in objects[0]:
            metadata = {
                "metadata": {
                    "format": "uDATA",
                    "version": "1.0",
                    "generated": datetime.now().isoformat(),
                    "source_file": input_file,
                    "records": len(objects),
                    "description": "Converted from formatted JSON to uDATA format"
                }
            }
            records_to_write.append(metadata)

        # Add all objects
        records_to_write.extend(objects)

        # Write to uDATA format
        with open(output_file, 'w') as f:
            for obj in records_to_write:
                f.write(json.dumps(obj, separators=(',', ':')) + '\n')

        print(f"✅ Converted {len(objects)} objects to {output_file}")
        print(f"📊 Total records written: {len(records_to_write)}")
        return True

    except Exception as e:
        print(f"❌ Error converting file: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 convert-formatted-json.py <input_file> <output_file>")
        print("Converts formatted JSON with multiple objects to uDATA format")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    success = convert_formatted_to_udata(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
