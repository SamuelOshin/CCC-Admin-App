#!/usr/bin/env python
"""
Database Performance Optimization Script

This script helps optimize database performance for large datasets by:
1. Creating recommended indexes
2. Analyzing query performance
3. Providing optimization recommendations

Usage:
    python optimize_database.py [--create-indexes] [--analyze-queries] [--dry-run]
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.core.management.color import no_style

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cccadminapp.settings')
django.setup()

def create_indexes(dry_run=False):
    """Create performance indexes for large datasets"""

    indexes = [
        # Clergy indexes
        {
            'name': 'idx_clergy_name_search',
            'table': 'clergy_registration_clergydetails',
            'columns': ['first_name', 'last_name'],
            'description': 'Index for clergy name searches'
        },
        {
            'name': 'idx_clergy_reg_number',
            'table': 'clergy_registration_clergydetails',
            'columns': ['reg_number'],
            'description': 'Index for clergy registration number searches'
        },
        {
            'name': 'idx_clergy_email',
            'table': 'clergy_registration_clergydetails',
            'columns': ['email'],
            'description': 'Index for clergy email searches'
        },
        {
            'name': 'idx_clergy_status',
            'table': 'clergy_registration_clergydetails',
            'columns': ['status'],
            'description': 'Index for clergy status filtering'
        },

        # Parish indexes
        {
            'name': 'idx_parish_name',
            'table': 'ParishRestructure_parishdirectory',
            'columns': ['name'],
            'description': 'Index for parish name searches'
        },
        {
            'name': 'idx_parish_address',
            'table': 'ParishRestructure_parishdirectory',
            'columns': ['address'],
            'description': 'Index for parish address searches'
        },
        {
            'name': 'idx_parish_email',
            'table': 'ParishRestructure_parishdirectory',
            'columns': ['email'],
            'description': 'Index for parish email searches'
        },
        {
            'name': 'idx_parish_register_status',
            'table': 'ParishRestructure_parishdirectory',
            'columns': ['register_status'],
            'description': 'Index for parish registration status'
        },
    ]

    print("🔧 Creating Database Indexes for Performance Optimization")
    print("=" * 60)

    with connection.cursor() as cursor:
        for index in indexes:
            try:
                # Check if index already exists
                cursor.execute("""
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = %s AND indexname = %s
                """, [index['table'], index['name']])

                if cursor.fetchone():
                    print(f"✅ Index {index['name']} already exists - skipping")
                    continue

                # Create index
                columns_str = ', '.join(index['columns'])
                sql = f"CREATE INDEX CONCURRENTLY {index['name']} ON {index['table']} ({columns_str});"

                if dry_run:
                    print(f"📋 DRY RUN: Would create index {index['name']}")
                    print(f"   SQL: {sql}")
                else:
                    print(f"🔨 Creating index: {index['name']}")
                    print(f"   Table: {index['table']}")
                    print(f"   Columns: {columns_str}")
                    print(f"   Purpose: {index['description']}")

                    cursor.execute(sql)
                    print("   ✅ Index created successfully")

            except Exception as e:
                print(f"❌ Error creating index {index['name']}: {str(e)}")

    print("\n🎉 Index creation completed!")

def analyze_query_performance():
    """Analyze current query performance"""

    print("📊 Analyzing Query Performance")
    print("=" * 40)

    queries = [
        {
            'name': 'Clergy Count Query',
            'sql': 'SELECT COUNT(*) FROM clergy_registration_clergydetails;'
        },
        {
            'name': 'Parish Count Query',
            'sql': 'SELECT COUNT(*) FROM ParishRestructure_parishdirectory;'
        },
        {
            'name': 'Clergy Search Query',
            'sql': "SELECT * FROM clergy_registration_clergydetails WHERE first_name ILIKE '%john%' LIMIT 10;"
        },
        {
            'name': 'Parish Search Query',
            'sql': "SELECT * FROM ParishRestructure_parishdirectory WHERE name ILIKE '%st%' LIMIT 10;"
        }
    ]

    with connection.cursor() as cursor:
        for query in queries:
            try:
                print(f"\n🔍 Analyzing: {query['name']}")
                print(f"   SQL: {query['sql'][:60]}...")

                # Execute with EXPLAIN ANALYZE
                explain_sql = f"EXPLAIN ANALYZE {query['sql']}"
                cursor.execute(explain_sql)

                results = cursor.fetchall()
                for row in results:
                    print(f"   {row[0]}")

            except Exception as e:
                print(f"❌ Error analyzing query: {str(e)}")

def show_recommendations():
    """Show optimization recommendations"""

    print("\n💡 Performance Optimization Recommendations")
    print("=" * 50)

    recommendations = [
        "1. Database Indexes:",
        "   - Add indexes on frequently searched fields (name, email, reg_number)",
        "   - Use composite indexes for common search patterns",
        "   - Monitor index usage and remove unused indexes",

        "2. Query Optimization:",
        "   - Use SELECT only() to fetch required fields",
        "   - Use select_related() for foreign key relationships",
        "   - Avoid N+1 query problems with prefetch_related()",

        "3. Caching Strategy:",
        "   - Cache expensive statistics for 10-15 minutes",
        "   - Use Redis for distributed caching in production",
        "   - Cache template fragments for frequently accessed data",

        "4. Database Configuration:",
        "   - Increase work_mem for complex queries",
        "   - Configure proper connection pooling",
        "   - Set appropriate maintenance_work_mem for index creation",

        "5. Monitoring:",
        "   - Monitor slow query logs",
        "   - Track cache hit rates",
        "   - Set up performance alerts"
    ]

    for rec in recommendations:
        print(rec)

def main():
    """Main function"""

    import argparse

    parser = argparse.ArgumentParser(description='Database Performance Optimization Tool')
    parser.add_argument('--create-indexes', action='store_true', help='Create performance indexes')
    parser.add_argument('--analyze-queries', action='store_true', help='Analyze query performance')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--recommendations', action='store_true', help='Show optimization recommendations')

    args = parser.parse_args()

    if not any([args.create_indexes, args.analyze_queries, args.recommendations]):
        print("Usage: python optimize_database.py [options]")
        print("\nOptions:")
        print("  --create-indexes    Create performance indexes")
        print("  --analyze-queries   Analyze current query performance")
        print("  --dry-run          Show what would be done without executing")
        print("  --recommendations   Show optimization recommendations")
        return

    if args.create_indexes:
        create_indexes(dry_run=args.dry_run)

    if args.analyze_queries:
        analyze_query_performance()

    if args.recommendations:
        show_recommendations()

if __name__ == '__main__':
    main()