#!/usr/bin/env python3
"""
Setup all sample data for Planora API
Runs all sample data scripts in the correct order
"""

import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """Run a sample data script and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    script_path = Path(__file__).parent / script_name
    
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent.parent,  # Run from project root
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"[SUCCESS] {script_name} completed successfully")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
        else:
            print(f"[FAILED] {script_name} failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {script_name} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to run {script_name}: {e}")
        return False
    
    return True

def main():
    """Main function to run all sample data scripts"""
    print("Planora API Sample Data Setup")
    print("This script will create comprehensive sample data for the Planora API")
    print("\nThis includes:")
    print("  • Sample users with different roles")
    print("  • Projects, tasks, and sprints")
    print("  • Time tracking and resource data")
    print("  • Integration and automation configurations")
    print("  • Reports and analytics data")
    
    # Confirm before proceeding
    response = input("\nDo you want to proceed? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    print(f"\nStarting sample data setup...")
    
    # List of scripts to run in order
    scripts = [
        ("seed_sample_users.py", "Create sample users, roles, and tenant"),
        ("seed_comprehensive_data.py", "Create projects, tasks, time tracking, integrations, reports")
    ]
    
    success_count = 0
    total_scripts = len(scripts)
    
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"\n[FAILED] Failed to run {script_name}. Stopping setup.")
            break
    
    print(f"\n{'='*60}")
    print("SETUP SUMMARY")
    print(f"{'='*60}")
    
    if success_count == total_scripts:
        print(f"[SUCCESS] All {total_scripts} scripts completed successfully!")
        print("\nSample data has been created with:")
        print("   - 8 sample users (password: Applogiq@123)")
        print("   - 5 projects with 45 tasks")
        print("   - 9 sprints and 3 kanban boards")
        print("   - 74 time entries and 5 timesheets")
        print("   - 5 integration providers")
        print("   - 4 automation rules and 3 webhooks")
        print("   - 5 reports and 1 dashboard")
        print("   - Analytics and metrics data")
        
        print(f"\nYou can now:")
        print("   - Access the API at: http://localhost:8000")
        print("   - View API docs at: http://localhost:8000/docs")
        print("   - Login with any sample user (password: Applogiq@123)")
        print("   - Explore projects, tasks, and all features")
        
    else:
        print(f"[PARTIAL] {success_count}/{total_scripts} scripts completed")
        print("Some sample data may not be available.")
        
        if success_count > 0:
            print(f"\nSuccessfully completed:")
            for i in range(success_count):
                script_name, description = scripts[i]
                print(f"   - {script_name}: {description}")
    
    print(f"\nFor more information, see: sample_data/README.md")

if __name__ == "__main__":
    main()