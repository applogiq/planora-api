#!/usr/bin/env python3
"""
Migration Script: Verify Mock Data
This script verifies the integrity and completeness of mock data in the Planora database.
It checks data relationships, constraints, and ensures minimum data requirements are met.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

def verify_table_counts():
    """Verify that all tables have minimum required data"""
    print("\n📊 Verifying table row counts...")

    required_counts = {
        "tbl_master_priority": 5,
        "tbl_master_project_status": 5,
        "tbl_master_project_type": 5,
        "tbl_master_project_methodology": 5,
        "tbl_roles": 5,
        "tbl_users": 25,
        "tbl_projects": 25,
        "tbl_project_epics": 25,
        "tbl_project_sprints": 25,
        "tbl_project_stories": 25,
        "tbl_project_backlog": 25,
        "tbl_audit_logs": 10
    }

    try:
        with SessionLocal() as session:
            results = {}
            total_tables = len(required_counts)
            passing_tables = 0

            for table, min_count in required_counts.items():
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    actual_count = result.scalar()

                    status = "✅" if actual_count >= min_count else "❌"
                    results[table] = {
                        'actual': actual_count,
                        'required': min_count,
                        'status': 'PASS' if actual_count >= min_count else 'FAIL'
                    }

                    if actual_count >= min_count:
                        passing_tables += 1

                    print(f"  {status} {table}: {actual_count}/{min_count} rows")

                except Exception as e:
                    print(f"  ❌ {table}: Error - {str(e)}")
                    results[table] = {'actual': 0, 'required': min_count, 'status': 'ERROR'}

            print(f"\n  📈 Summary: {passing_tables}/{total_tables} tables have sufficient data")
            return results, passing_tables == total_tables

    except Exception as e:
        print(f"  ❌ Error verifying table counts: {str(e)}")
        return {}, False

def verify_data_relationships():
    """Verify foreign key relationships and data integrity"""
    print("\n🔗 Verifying data relationships...")

    relationship_checks = [
        {
            'name': 'Users have valid roles',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_users u
                LEFT JOIN tbl_roles r ON u.role_id = r.id
                WHERE r.id IS NULL
            """,
            'expected': 0
        },
        {
            'name': 'Projects have valid team leads',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_projects p
                LEFT JOIN tbl_users u ON p.team_lead_id = u.id
                WHERE p.team_lead_id IS NOT NULL AND u.id IS NULL
            """,
            'expected': 0
        },
        {
            'name': 'Epics belong to valid projects',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_project_epics e
                LEFT JOIN tbl_projects p ON e.project_id = p.id
                WHERE p.id IS NULL
            """,
            'expected': 0
        },
        {
            'name': 'Sprints belong to valid projects',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_project_sprints s
                LEFT JOIN tbl_projects p ON s.project_id = p.id
                WHERE s.project_id IS NOT NULL AND p.id IS NULL
            """,
            'expected': 0
        },
        {
            'name': 'Stories have valid assignees',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_project_stories t
                LEFT JOIN tbl_users u ON t.assignee_id = u.id
                WHERE t.assignee_id IS NOT NULL AND u.id IS NULL
            """,
            'expected': 0
        },
        {
            'name': 'Backlog items belong to valid projects',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_project_backlog b
                LEFT JOIN tbl_projects p ON b.project_id = p.id
                WHERE b.project_id IS NOT NULL AND p.id IS NULL
            """,
            'expected': 0
        }
    ]

    try:
        with SessionLocal() as session:
            passed_checks = 0
            total_checks = len(relationship_checks)

            for check in relationship_checks:
                try:
                    result = session.execute(text(check['query']))
                    invalid_count = result.scalar()

                    if invalid_count == check['expected']:
                        print(f"  ✅ {check['name']}: PASS")
                        passed_checks += 1
                    else:
                        print(f"  ❌ {check['name']}: FAIL ({invalid_count} invalid records)")

                except Exception as e:
                    print(f"  ❌ {check['name']}: ERROR - {str(e)}")

            print(f"\n  🔗 Relationship Summary: {passed_checks}/{total_checks} checks passed")
            return passed_checks == total_checks

    except Exception as e:
        print(f"  ❌ Error verifying relationships: {str(e)}")
        return False

def verify_data_quality():
    """Verify data quality and business rules"""
    print("\n🎯 Verifying data quality...")

    quality_checks = [
        {
            'name': 'Users have valid email formats',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_users
                WHERE email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            """,
            'expected': 0
        },
        {
            'name': 'Projects have valid date ranges',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_projects
                WHERE start_date IS NOT NULL AND end_date IS NOT NULL
                AND start_date > end_date
            """,
            'expected': 0
        },
        {
            'name': 'Sprints have valid date ranges',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_project_sprints
                WHERE start_date IS NOT NULL AND end_date IS NOT NULL
                AND start_date > end_date
            """,
            'expected': 0
        },
        {
            'name': 'Projects have progress between 0-100',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_projects
                WHERE progress < 0 OR progress > 100
            """,
            'expected': 0
        },
        {
            'name': 'All active users have names',
            'query': """
                SELECT COUNT(*) as invalid_count
                FROM tbl_users
                WHERE is_active = true AND (name IS NULL OR name = '')
            """,
            'expected': 0
        }
    ]

    try:
        with SessionLocal() as session:
            passed_checks = 0
            total_checks = len(quality_checks)

            for check in quality_checks:
                try:
                    result = session.execute(text(check['query']))
                    invalid_count = result.scalar()

                    if invalid_count == check['expected']:
                        print(f"  ✅ {check['name']}: PASS")
                        passed_checks += 1
                    else:
                        print(f"  ❌ {check['name']}: FAIL ({invalid_count} invalid records)")

                except Exception as e:
                    print(f"  ❌ {check['name']}: ERROR - {str(e)}")

            print(f"\n  🎯 Quality Summary: {passed_checks}/{total_checks} checks passed")
            return passed_checks == total_checks

    except Exception as e:
        print(f"  ❌ Error verifying data quality: {str(e)}")
        return False

def get_data_statistics():
    """Get comprehensive statistics about the data"""
    print("\n📈 Generating data statistics...")

    try:
        with SessionLocal() as session:
            stats = {}

            # Get distribution of users by role
            result = session.execute(text("""
                SELECT r.name, COUNT(u.id) as user_count
                FROM tbl_roles r
                LEFT JOIN tbl_users u ON r.id = u.role_id
                GROUP BY r.id, r.name
                ORDER BY user_count DESC
            """))
            stats['users_by_role'] = result.fetchall()

            # Get project status distribution
            result = session.execute(text("""
                SELECT status, COUNT(*) as project_count
                FROM tbl_projects
                GROUP BY status
                ORDER BY project_count DESC
            """))
            stats['projects_by_status'] = result.fetchall()

            # Get story priority distribution
            result = session.execute(text("""
                SELECT priority, COUNT(*) as story_count
                FROM tbl_project_stories
                GROUP BY priority
                ORDER BY story_count DESC
            """))
            stats['stories_by_priority'] = result.fetchall()

            # Display statistics
            print(f"\n  👥 Users by Role:")
            for role_name, count in stats['users_by_role']:
                print(f"     {role_name}: {count} users")

            print(f"\n  📊 Projects by Status:")
            for status, count in stats['projects_by_status']:
                print(f"     {status}: {count} projects")

            print(f"\n  📋 Stories by Priority:")
            for priority, count in stats['stories_by_priority']:
                print(f"     {priority}: {count} stories")

            return stats

    except Exception as e:
        print(f"  ❌ Error generating statistics: {str(e)}")
        return {}

def main():
    """Main verification function"""
    print("=" * 80)
    print("🔍 PLANORA API - VERIFY MOCK DATA MIGRATION")
    print("=" * 80)
    print("This script will verify the mock data integrity:")
    print("  1. Table row counts (minimum 25 per table)")
    print("  2. Foreign key relationships")
    print("  3. Data quality and business rules")
    print("  4. Data distribution statistics")
    print("\n" + "=" * 80)

    # Track overall verification results
    verification_results = {
        'counts': False,
        'relationships': False,
        'quality': False
    }

    # 1. Verify table counts
    count_results, counts_passed = verify_table_counts()
    verification_results['counts'] = counts_passed

    # 2. Verify relationships
    relationships_passed = verify_data_relationships()
    verification_results['relationships'] = relationships_passed

    # 3. Verify data quality
    quality_passed = verify_data_quality()
    verification_results['quality'] = quality_passed

    # 4. Generate statistics
    stats = get_data_statistics()

    # Final summary
    total_checks = len(verification_results)
    passed_checks = sum(verification_results.values())

    print("\n" + "=" * 80)
    print("📋 VERIFICATION SUMMARY:")
    print("=" * 80)
    print(f"  📊 Row Count Verification: {'✅ PASS' if verification_results['counts'] else '❌ FAIL'}")
    print(f"  🔗 Relationship Verification: {'✅ PASS' if verification_results['relationships'] else '❌ FAIL'}")
    print(f"  🎯 Data Quality Verification: {'✅ PASS' if verification_results['quality'] else '❌ FAIL'}")
    print(f"\n  📈 Overall Score: {passed_checks}/{total_checks} verification areas passed")

    if passed_checks == total_checks:
        print(f"\n🎉 ALL VERIFICATIONS PASSED!")
        print(f"   Mock data is ready for use in development and testing")
        print("=" * 80)
        print("🎯 Database is ready! You can now:")
        print("  1. Start the API server: uvicorn main:app --reload --port 8000")
        print("  2. Access the API documentation at: http://localhost:8000/docs")
        print("  3. Begin development and testing")
        print("=" * 80)
        return True
    else:
        print(f"\n⚠️  VERIFICATION COMPLETED WITH ISSUES!")
        print(f"   {total_checks - passed_checks} verification area(s) failed")
        print("   Please review the issues above and re-run data insertion if needed")
        print("=" * 80)
        return False

if __name__ == "__main__":
    print("Starting mock data verification...")

    success = main()

    if not success:
        sys.exit(1)