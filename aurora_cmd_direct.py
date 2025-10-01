#!/usr/bin/env python3
"""
Direct Aurora PostgreSQL Connection via Command Line
This script connects directly to Aurora PostgreSQL and runs verification queries
"""

import sys
import os

# Add the virtual environment Python path
venv_python = r"D:\udacity\Lingala_Rajesh_ProjectSubmission\venv\Scripts\python.exe"

try:
    import psycopg2
    import psycopg2.extras
    print("✅ psycopg2 is available")
except ImportError:
    print("❌ psycopg2 not available")
    print("Installing psycopg2-binary...")
    os.system(f'"{venv_python}" -m pip install psycopg2-binary')
    try:
        import psycopg2
        import psycopg2.extras
        print("✅ psycopg2 installed successfully")
    except ImportError:
        print("❌ Failed to install psycopg2")
        sys.exit(1)

def connect_to_aurora():
    """Connect to Aurora PostgreSQL database"""
    
    # Connection parameters
    conn_params = {
        'host': 'my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com',
        'port': 5432,
        'database': 'myapp',
        'user': 'dbadmin',
        'password': '%252m!KjPM$(5[LX'
    }
    
    try:
        print("🔌 Connecting to Aurora PostgreSQL...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        print("✅ Connected successfully!")
        return conn, cursor
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def run_query(cursor, query_name, query_sql):
    """Run a query and display results"""
    print(f"\n📊 {query_name}")
    print("=" * 60)
    
    try:
        cursor.execute(query_sql)
        results = cursor.fetchall()
        
        if results:
            # Get column names
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                
                # Print header
                header = " | ".join(f"{col:<15}" for col in columns)
                print(header)
                print("-" * len(header))
                
                # Print rows
                for row in results:
                    row_str = " | ".join(f"{str(val):<15}" for val in row)
                    print(row_str)
                
                print(f"\nFound {len(results)} records")
            else:
                print("Query executed successfully (no results returned)")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"❌ Query failed: {e}")

def run_verification_queries():
    """Run all verification queries"""
    
    conn, cursor = connect_to_aurora()
    if not conn or not cursor:
        return False
    
    try:
        # Query 1: Check database version
        run_query(cursor, "DATABASE VERSION", "SELECT version();")
        
        # Query 2: Check extensions
        run_query(cursor, "INSTALLED EXTENSIONS", "SELECT * FROM pg_extension;")
        
        # Query 3: Check bedrock_integration schema tables
        run_query(cursor, "BEDROCK_INTEGRATION SCHEMA TABLES", """
            SELECT 
                table_schema || '.' || table_name as show_tables,
                table_type
            FROM 
                information_schema.tables 
            WHERE 
                table_type = 'BASE TABLE' 
            AND 
                table_schema = 'bedrock_integration';
        """)
        
        # Query 4: Check if vector extension is available
        run_query(cursor, "VECTOR EXTENSION CHECK", """
            SELECT * FROM pg_available_extensions WHERE name = 'vector';
        """)
        
        # Query 5: Check schemas
        run_query(cursor, "AVAILABLE SCHEMAS", """
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
        """)
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Verification queries completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running verification queries: {e}")
        return False

def setup_vector_database():
    """Set up vector database if needed"""
    
    conn, cursor = connect_to_aurora()
    if not conn or not cursor:
        return False
    
    try:
        print("\n🛠️ Setting up vector database...")
        
        # Enable autocommit for extension creation
        conn.autocommit = True
        
        setup_queries = [
            ("Creating vector extension", "CREATE EXTENSION IF NOT EXISTS vector;"),
            ("Creating bedrock_integration schema", "CREATE SCHEMA IF NOT EXISTS bedrock_integration;"),
            ("Creating bedrock_kb table", """
                CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    embedding vector(1536),
                    chunks text NOT NULL,
                    metadata jsonb,
                    source_file varchar(255),
                    created_at timestamp DEFAULT CURRENT_TIMESTAMP
                );
            """),
            ("Creating HNSW index", """
                CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx 
                ON bedrock_integration.bedrock_kb 
                USING hnsw (embedding vector_cosine_ops);
            """)
        ]
        
        for step_name, query in setup_queries:
            print(f"   {step_name}...")
            try:
                cursor.execute(query)
                print(f"   ✅ {step_name} completed")
            except Exception as e:
                print(f"   ⚠️ {step_name} failed: {e}")
        
        cursor.close()
        conn.close()
        
        print("🎉 Vector database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up vector database: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Aurora PostgreSQL Direct Connection Tool")
    print("=" * 50)
    
    print("\n🔍 Running verification queries...")
    if run_verification_queries():
        
        print("\n🛠️ Do you want to set up the vector database? (y/n)")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes']:
            setup_vector_database()
            
            # Run verification again to show the changes
            print("\n🔍 Running verification queries again to show changes...")
            run_verification_queries()
    
    print("\n✅ Command line database connection tool completed!")

if __name__ == "__main__":
    main()