#!/usr/bin/env python3
"""
Setup Organizer for Planora API
This script runs the existing setup scripts in the correct order
"""

import sys
import os
import subprocess
from pathlib import Path

def run_setup_step(script_name, description):
    """Run a setup script and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run([sys.executable, f"setup/{script_name}"],
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent)

        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def main():
    """Run all setup scripts in correct order"""

    print("=" * 80)
    print("🚀 PLANORA API - SETUP ORGANIZER")
    print("=" * 80)
    print("Running existing setup scripts in correct order...")
    print("=" * 80)

    steps = [
        ("create_db.py", "Creating Database Tables"),
        ("insert_master_data.py", "Inserting Master Data"),
        ("insert_user_data.py", "Inserting User Data"),
        ("insert_all_project_data.py", "Inserting Project Data"),
        ("insert_backlog_data.py", "Inserting Backlog Data")
    ]

    success_count = 0

    for script, description in steps:
        if run_setup_step(script, description):
            success_count += 1
        else:
            print(f"⚠️  Continuing with next step despite failure...")

    print("\n" + "=" * 80)
    print(f"📊 SETUP SUMMARY: {success_count}/{len(steps)} steps completed successfully")

    if success_count == len(steps):
        print("🎉 ALL SETUP COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️  Some steps had issues, but setup continued")

    print("\n💡 NEXT STEPS:")
    print("   1. Start server: uvicorn main:app --reload --port 8000")
    print("   2. API docs: http://localhost:8000/docs")
    print("=" * 80)

if __name__ == "__main__":
    main()