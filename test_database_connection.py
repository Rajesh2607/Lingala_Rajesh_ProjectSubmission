#!/usr/bin/env python3
"""
Database Query Executor for Aurora PostgreSQL
Tests database connectivity and runs verification queries
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

def get_database_credentials():
    """Get database credentials from AWS Secrets Manager"""
    try:
        secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-1NyjuJ"
        secretsmanager = boto3.client('secretsmanager', region_name='us-west-2')
        
        response = secretsmanager.get_secret_value(SecretId=secret_arn)
        secret_data = json.loads(response['SecretString'])
        
        return {
            'host': secret_data.get('host', 'my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com'),
            'database': secret_data.get('db', 'myapp'),
            'username': secret_data.get('username', 'dbadmin'),
            'password': secret_data.get('password'),
            'port': secret_data.get('port', 5432)
        }
    except ClientError as e:
        print(f"❌ Error getting credentials: {e}")
        return None

def run_verification_queries_direct(conn_info):
    """Run verification queries using direct database connection"""
    if not PSYCOPG2_AVAILABLE:
        print("❌ psycopg2 not available. Please install it with: pip install psycopg2-binary")
        return False
    
    try:
        # Connect to database
        print("🔗 Connecting to Aurora PostgreSQL...")
        conn = psycopg2.connect(
            host=conn_info['host'],
            database=conn_info['database'],
            user=conn_info['username'],
            password=conn_info['password'],
            port=conn_info['port']
        )
        
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        
        # Query 1: Check extensions
        print("\n📋 Query 1: Checking PostgreSQL extensions")
        print("=" * 50)
        cursor.execute("SELECT * FROM pg_extension;")
        extensions = cursor.fetchall()
        
        print("Extensions installed:")
        for ext in extensions:
            print(f"   - {ext[0]} (version: {ext[1]})")
            
        # Check specifically for vector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchall()
        if vector_ext:
            print("✅ Vector extension is installed!")
        else:
            print("❌ Vector extension is NOT installed!")
        
        # Query 2: Check bedrock_integration schema tables
        print("\n📋 Query 2: Checking bedrock_integration schema")
        print("=" * 50)
        cursor.execute("""
            SELECT table_schema || '.' || table_name as show_tables
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            AND table_schema = 'bedrock_integration'
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("Tables in bedrock_integration schema:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("❌ No tables found in bedrock_integration schema")
        
        # Query 3: Check all schemas
        print("\n📋 Query 3: All available schemas")
        print("=" * 50)
        cursor.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;")
        schemas = cursor.fetchall()
        print("Available schemas:")
        for schema in schemas:
            print(f"   - {schema[0]}")
        
        # Query 4: Check database version and settings
        print("\n📋 Query 4: Database information")
        print("=" * 50)
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        cursor.execute("SHOW shared_preload_libraries;")
        libs = cursor.fetchone()
        print(f"Shared preload libraries: {libs[0]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def provide_manual_instructions(conn_info):
    """Provide manual instructions for running queries"""
    print("\n" + "=" * 70)
    print("📝 MANUAL DATABASE QUERY INSTRUCTIONS")
    print("=" * 70)
    
    if conn_info:
        print(f"\n🔗 Connection Information:")
        print(f"   Host: {conn_info['host']}")
        print(f"   Database: {conn_info['database']}")
        print(f"   Username: {conn_info['username']}")
        print(f"   Port: {conn_info['port']}")
        print("   Password: (retrieved from AWS Secrets Manager)")
    
    print(f"\n📋 SQL Queries to Run:")
    print("=" * 40)
    
    queries = [
        ("Check all extensions", "SELECT * FROM pg_extension;"),
        ("Check vector extension specifically", "SELECT * FROM pg_extension WHERE extname = 'vector';"),
        ("Check bedrock_integration tables", """
SELECT table_schema || '.' || table_name as show_tables
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
AND table_schema = 'bedrock_integration';"""),
        ("Check all schemas", "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;"),
        ("Check database version", "SELECT version();"),
        ("Check shared libraries", "SHOW shared_preload_libraries;")
    ]
    
    for i, (desc, query) in enumerate(queries, 1):
        print(f"\n{i}. {desc}:")
        print("   " + query.replace("\n", "\n   "))
    
    print(f"\n🔧 To set up the vector database, run all commands from:")
    print("   setup_vector_database.sql")
    
    print(f"\n💡 AWS RDS Query Editor Steps:")
    print("   1. Go to AWS Console → RDS → Databases")
    print("   2. Click on 'my-aurora-serverless'")
    print("   3. Click 'Query Editor' tab")
    print("   4. Connect using database credentials")
    print("   5. Run the SQL commands above")

def main():
    print("🔍 Aurora PostgreSQL Database Verification")
    print("=" * 50)
    
    # Get database credentials
    conn_info = get_database_credentials()
    if not conn_info:
        print("❌ Cannot retrieve database credentials")
        sys.exit(1)
    
    print("✅ Database credentials retrieved successfully")
    
    # Try direct connection first
    if PSYCOPG2_AVAILABLE:
        print("\n🚀 Attempting direct database connection...")
        success = run_verification_queries_direct(conn_info)
        if success:
            return
    else:
        print("\n⚠️  psycopg2 not available for direct connection")
        print("Install with: pip install psycopg2-binary")
    
    # Provide manual instructions
    provide_manual_instructions(conn_info)
    
    print(f"\n" + "=" * 70)
    print("🎯 NEXT STEPS")
    print("=" * 70)
    print("1. Connect to Aurora PostgreSQL using AWS RDS Query Editor")
    print("2. Run the setup commands from setup_vector_database.sql")
    print("3. Run the verification queries listed above")
    print("4. Confirm vector extension and bedrock_integration schema are set up")
    print("5. The database will be ready for Bedrock Knowledge Base integration")

if __name__ == "__main__":
    main()