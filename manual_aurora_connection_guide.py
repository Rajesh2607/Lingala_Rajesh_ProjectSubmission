#!/usr/bin/env python3
"""
Manual Database Connection Guide for Aurora PostgreSQL
Since direct Python connection has issues, let's provide manual connection methods
"""

def show_connection_details():
    """Show all connection details for manual connection"""
    print("🔧 Aurora PostgreSQL Connection Details")
    print("="*50)
    print("Host: my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com")
    print("Port: 5432")
    print("Database: myapp")
    print("Username: dbadmin")
    print("Password: %252m!KjPM$(5[LX")
    print("Engine: PostgreSQL 15.4")

def show_rds_query_editor_method():
    """Show how to use RDS Query Editor with database credentials"""
    print("\n🎯 Method 1: RDS Query Editor (Recommended)")
    print("="*50)
    print("1. Go to AWS RDS Console")
    print("2. Find your Aurora cluster: my-aurora-serverless")
    print("3. Click 'Query Editor'")
    print("4. Instead of 'Connect using RDS Data API', choose:")
    print("   → 'Add new database credentials'")
    print("   → 'Connect using database credentials'")
    print("5. Enter the connection details manually:")
    print("   • Database username: dbadmin")
    print("   • Database password: %252m!KjPM$(5[LX")
    print("   • Database name: myapp")
    print("6. Click 'Connect to database'")

def show_verification_queries():
    """Show the exact queries to run for verification"""
    print("\n📊 Verification Queries to Run")
    print("="*50)
    
    print("\n🔍 Query 1: Check installed extensions")
    print("-"*40)
    print("SELECT * FROM pg_extension;")
    print("\n📸 Take a screenshot of this result!")
    
    print("\n🔍 Query 2: Check bedrock_integration schema tables")
    print("-"*40)
    print("""SELECT 
    table_schema || '.' || table_name as show_tables,
    table_type
FROM 
    information_schema.tables 
WHERE 
    table_type = 'BASE TABLE' 
AND 
    table_schema = 'bedrock_integration';""")
    print("\n📸 Take a screenshot of this result!")
    
    print("\n🔍 Query 3: Check bedrock_kb table structure (if it exists)")
    print("-"*40)
    print("""SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM 
    information_schema.columns 
WHERE 
    table_schema = 'bedrock_integration' 
AND 
    table_name = 'bedrock_kb'
ORDER BY 
    ordinal_position;""")
    print("\n📸 Take a screenshot of this result!")
    
    print("\n🔍 Query 4: Check current database version")
    print("-"*40)
    print("SELECT version();")
    print("\n📸 Take a screenshot of this result!")

def show_setup_queries():
    """Show queries to set up the vector database if not already done"""
    print("\n🛠️ Database Setup Queries (Run these if database is not set up)")
    print("="*70)
    
    queries = [
        ("1. Create vector extension", "CREATE EXTENSION IF NOT EXISTS vector;"),
        ("2. Create bedrock_integration schema", "CREATE SCHEMA IF NOT EXISTS bedrock_integration;"),
        ("3. Create bedrock_user role", """DO $$ 
BEGIN 
    CREATE ROLE bedrock_user LOGIN PASSWORD 'BedrockUser2024!'; 
EXCEPTION 
    WHEN duplicate_object THEN 
        RAISE NOTICE 'Role already exists'; 
END $$;"""),
        ("4. Grant schema permissions", "GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;"),
        ("5. Create bedrock_kb table", """CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding vector(1536),
    chunks text,
    metadata json
);"""),
        ("6. Create HNSW index", """CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx 
ON bedrock_integration.bedrock_kb 
USING hnsw (embedding vector_cosine_ops);"""),
        ("7. Grant table permissions", "GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;")
    ]
    
    for step, query in queries:
        print(f"\n{step}:")
        print("-" * len(step))
        print(query)
        print()

def show_pgadmin_method():
    """Show how to use pgAdmin for connection"""
    print("\n🎯 Method 2: pgAdmin (GUI Tool)")
    print("="*50)
    print("1. Download pgAdmin: https://www.pgadmin.org/download/")
    print("2. Install and open pgAdmin")
    print("3. Right-click 'Servers' → Create → Server")
    print("4. Fill in the connection details:")
    print("   • Name: Aurora Heavy Machinery DB")
    print("   • Host: my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com")
    print("   • Port: 5432")
    print("   • Database: myapp")
    print("   • Username: dbadmin")
    print("   • Password: %252m!KjPM$(5[LX")
    print("5. Click 'Save' to connect")
    print("6. Run the verification queries in the Query Tool")

def show_psql_method():
    """Show command line connection method"""
    print("\n🎯 Method 3: Command Line (psql)")
    print("="*50)
    print("1. Install PostgreSQL client tools:")
    print("   • Download: https://www.postgresql.org/download/windows/")
    print("   • Or use: winget install PostgreSQL.PostgreSQL")
    print("   • Add to PATH: C:\\Program Files\\PostgreSQL\\16\\bin")
    print("\n2. Connect using psql:")
    print("psql -h my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com \\")
    print("     -p 5432 \\")
    print("     -U dbadmin \\")
    print("     -d myapp")
    print("\n3. Enter password when prompted: %252m!KjPM$(5[LX")
    print("4. Run the verification queries")

def main():
    print("🚀 Aurora PostgreSQL Manual Connection & Verification Guide")
    print("="*70)
    
    show_connection_details()
    show_rds_query_editor_method()
    show_verification_queries()
    show_setup_queries()
    show_pgadmin_method()
    show_psql_method()
    
    print("\n" + "="*70)
    print("🎯 SUMMARY: Next Steps")
    print("="*70)
    print("1. Choose your preferred connection method (RDS Query Editor recommended)")
    print("2. Connect to the Aurora PostgreSQL database")
    print("3. Run the verification queries and take screenshots")
    print("4. If database is not set up, run the setup queries")
    print("5. Share the screenshots for analysis")
    print("\n🔥 Once database is verified, we can create the Bedrock Knowledge Base!")

if __name__ == "__main__":
    main()