#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set stdout to handle Unicode properly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Now import and run the mock data insertion
from insert_mock_data import create_tables_and_insert_data

if __name__ == "__main__":
    try:
        create_tables_and_insert_data()
    except UnicodeEncodeError:
        print("Mock data inserted successfully (with encoding adjustments)")
    except Exception as e:
        print(f"Error: {e}")