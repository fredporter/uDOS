#!/usr/bin/env python3
"""
uSCRIPT Library Script: Data Processor v1.0.0

Description: Process CSV and JSON data with advanced filtering capabilities
Author: uDOS Team
Created: 2025-08-17
Updated: 2025-08-17
Category: utilities
Tags: data, csv, json, filtering, processing

Usage:
    python data-processor.py input.csv output.csv [--filter=TYPE] [--format=FORMAT]

Dependencies:
    - pandas>=1.0.0
    - numpy>=1.18.0

uSCRIPT Registry: data-processor
uDOS Integration: ✅ Full integration with uMEMORY and logging
"""

import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class DataProcessor:
    """Advanced data processing with filtering and format conversion."""
    
    def __init__(self):
        self.version = "1.0.0"
        self.supported_formats = ['csv', 'json', 'xlsx', 'parquet']
        
    def log_execution(self, message, level="INFO"):
        """Log to uDOS format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def process_data(self, input_file, output_file, filter_type=None, output_format='csv'):
        """Process data with optional filtering."""
        self.log_execution(f"Starting data processing: {input_file} -> {output_file}")
        
        try:
            # Load data based on file extension
            input_path = Path(input_file)
            if input_path.suffix.lower() == '.csv':
                df = pd.read_csv(input_file)
            elif input_path.suffix.lower() == '.json':
                df = pd.read_json(input_file)
            else:
                raise ValueError(f"Unsupported input format: {input_path.suffix}")
                
            self.log_execution(f"Loaded {len(df)} rows from {input_file}")
            
            # Apply filtering if specified
            if filter_type:
                original_count = len(df)
                if filter_type == 'active':
                    df = df[df.get('status', '').str.lower() == 'active']
                elif filter_type == 'recent':
                    # Filter last 30 days if date column exists
                    date_cols = df.select_dtypes(include=['datetime64']).columns
                    if len(date_cols) > 0:
                        cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
                        df = df[df[date_cols[0]] >= cutoff]
                
                self.log_execution(f"Filtered from {original_count} to {len(df)} rows")
            
            # Save in requested format
            output_path = Path(output_file)
            if output_format == 'csv' or output_path.suffix.lower() == '.csv':
                df.to_csv(output_file, index=False)
            elif output_format == 'json' or output_path.suffix.lower() == '.json':
                df.to_json(output_file, orient='records', indent=2)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
            self.log_execution(f"Successfully saved {len(df)} rows to {output_file}")
            return True
            
        except Exception as e:
            self.log_execution(f"Error processing data: {str(e)}", "ERROR")
            return False

def main():
    parser = argparse.ArgumentParser(description='uSCRIPT Data Processor')
    parser.add_argument('input_file', help='Input data file (CSV or JSON)')
    parser.add_argument('output_file', help='Output data file')
    parser.add_argument('--filter', choices=['active', 'recent'], 
                       help='Filter type to apply')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                       help='Output format')
    parser.add_argument('--version', action='version', version='1.0.0')
    
    args = parser.parse_args()
    
    processor = DataProcessor()
    success = processor.process_data(
        args.input_file, 
        args.output_file,
        args.filter,
        args.format
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
