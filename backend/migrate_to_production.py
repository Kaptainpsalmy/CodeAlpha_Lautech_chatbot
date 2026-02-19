"""
Run this script to migrate your local SQLite data to production PostgreSQL
"""

import os
import sys
from database.production import init_production_db, migrate_from_sqlite

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LAUTECH Chatbot - Production Migration Tool")
    print("=" * 60)

    # Check if SQLite database exists
    sqlite_path = os.path.join(os.path.dirname(__file__), '../data/lautech.db')
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found at {sqlite_path}")
        print("Please run the development version first to create the database.")
        sys.exit(1)

    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set!")
        print("\nPlease set your PostgreSQL connection string:")
        print("export DATABASE_URL='postgresql://user:password@host:port/dbname'")
        print("\nOr on Windows:")
        print("set DATABASE_URL=postgresql://user:password@host:port/dbname")
        sys.exit(1)

    print("\n📊 Source: SQLite database")
    print(f"   Path: {sqlite_path}")
    print("\n🎯 Target: PostgreSQL")
    print(f"   URL: {os.environ.get('DATABASE_URL')}")

    print("\n🔄 Starting migration...")

    # Initialize production database
    init_production_db()

    # Migrate data
    migrate_from_sqlite()

    print("\n✅ Migration complete!")
    print("Your data is now in production!")