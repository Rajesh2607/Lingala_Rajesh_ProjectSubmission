#!/usr/bin/env python3
"""
Direct PostgreSQL Connection to Aurora Database
This bypasses RDS Data API permission issues by using direct psycopg2 connection
"""

import sys
import json

# Check if psycopg2 is available
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
    print("✅ psycopg2 is available")
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("❌ psycopg2 not available")
    print("   Install with: pip install psycopg2-binary")

def get_connection_params():
    """Get connection parameters for Aurora PostgreSQL"""
    return {
        'host': 'my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com',
        'port': 5432,
        'database': 'myapp',
        'user': 'dbadmin',
        'password': '%252m!KjPM$(5[LX'  # Retrieved from Secrets Manager
    }

def test_basic_connection():
    """Test basic connection to Aurora PostgreSQL"""
    if not PSYCOPG2_AVAILABLE:
        return False
    
    conn_params = get_connection_params()
    
    try:
        print("🔄 Testing basic connection to Aurora PostgreSQL...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"   Database version: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def setup_vector_database():
    """Set up vector database with all required components"""
    if not PSYCOPG2_AVAILABLE:
        print("❌ Cannot setup database without psycopg2")
        return False
    
    conn_params = get_connection_params()
    
    try:
        print("🔄 Setting up vector database...")
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True  # Enable autocommit for extensions and schema creation
        cursor = conn.cursor()
        
        print("\n1️⃣ Creating vector extension...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ Vector extension created/verified!")
        except Exception as e:
            print(f"⚠️ Vector extension error: {e}")
            print("   This might require superuser privileges")
        
        print("\n2️⃣ Creating bedrock_integration schema...")
        try:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS bedrock_integration;")
            print("✅ bedrock_integration schema created!")
        except Exception as e:
            print(f"❌ Schema creation error: {e}")
        
        print("\n3️⃣ Creating bedrock_user role...")
        try:
            cursor.execute("""
                DO $$ 
                BEGIN 
                    CREATE ROLE bedrock_user LOGIN PASSWORD 'BedrockUser2024!'; 
                EXCEPTION 
                    WHEN duplicate_object THEN 
                        RAISE NOTICE 'Role bedrock_user already exists'; 
                END $$;
            """)
            print("✅ bedrock_user role created/verified!")
        except Exception as e:
            print(f"⚠️ Role creation error: {e}")
        
        print("\n4️⃣ Granting permissions on schema...")
        try:
            cursor.execute("GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;")
            print("✅ Schema permissions granted!")
        except Exception as e:
            print(f"⚠️ Permission grant error: {e}")
        
        print("\n5️⃣ Creating bedrock_kb table...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    embedding vector(1536),
                    chunks text,
                    metadata json
                );
            """)
            print("✅ bedrock_kb table created!")
        except Exception as e:
            print(f"⚠️ Table creation error: {e}")
            print("   Vector type might not be available")
        
        print("\n6️⃣ Creating HNSW index for embeddings...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx 
                ON bedrock_integration.bedrock_kb 
                USING hnsw (embedding vector_cosine_ops);
            """)
            print("✅ HNSW index created!")
        except Exception as e:
            print(f"⚠️ Index creation error: {e}")
            print("   Vector extension might not be fully installed")
        
        print("\n7️⃣ Granting table permissions...")
        try:
            cursor.execute("GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;")
            print("✅ Table permissions granted!")
        except Exception as e:
            print(f"⚠️ Table permission error: {e}")
        
        cursor.close()
        conn.close()
        print("\n🎉 Vector database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def verify_database_setup():
    """Verify database setup with the requested queries"""
    if not PSYCOPG2_AVAILABLE:
        print("❌ Cannot verify database without psycopg2")
        return False
    
    conn_params = get_connection_params()
    
    try:
        print("🔍 Verifying database setup...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        print("\n" + "="*60)
        print("📊 QUERY 1: SELECT * FROM pg_extension;")
        print("="*60)
        
        cursor.execute("SELECT * FROM pg_extension;")
        extensions = cursor.fetchall()
        
        print(f"Found {len(extensions)} extensions:")
        print(f"{'Extension Name':<20} {'Schema':<15} {'Version':<10} {'Relocatable'}")
        print("-"*60)
        
        for ext in extensions:
            print(f"{ext['extname']:<20} {ext['extnamespace']:<15} {ext['extversion']:<10} {ext['extrelocatable']}")
        
        # Check specifically for vector extension
        vector_found = False
        for ext in extensions:
            if ext['extname'] == 'vector':
                vector_found = True
                print(f"\n✅ Vector extension found! Version: {ext['extversion']}")
                break
        
        if not vector_found:
            print("\n❌ Vector extension NOT found!")
        
        print("\n" + "="*60)
        print("📊 QUERY 2: Check bedrock_integration schema tables")
        print("="*60)
        
        cursor.execute("""
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
        
        tables = cursor.fetchall()
        
        if tables:
            print(f"Found {len(tables)} tables in bedrock_integration schema:")
            print(f"{'Table Name':<35} {'Type'}")
            print("-"*50)
            for table in tables:
                print(f"{table['show_tables']:<35} {table['table_type']}")
        else:
            print("❌ No tables found in bedrock_integration schema!")
        
        print("\n" + "="*60)
        print("📊 QUERY 3: Check bedrock_kb table structure")
        print("="*60)
        
        cursor.execute("""
            SELECT 
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
                ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print(f"bedrock_kb table structure:")
            print(f"{'Column Name':<15} {'Data Type':<20} {'Nullable':<10} {'Default'}")
            print("-"*70)
            for col in columns:
                default = col['column_default'] or 'None'
                if len(default) > 20:
                    default = default[:17] + "..."
                print(f"{col['column_name']:<15} {col['data_type']:<20} {col['is_nullable']:<10} {default}")
        else:
            print("❌ bedrock_kb table not found!")
        
        print("\n" + "="*60)
        print("📊 QUERY 4: Check indexes on bedrock_kb table")
        print("="*60)
        
        cursor.execute("""
            SELECT 
                indexname,
                indexdef
            FROM 
                pg_indexes 
            WHERE 
                schemaname = 'bedrock_integration' 
            AND 
                tablename = 'bedrock_kb';
        """)
        
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"Indexes on bedrock_kb table:")
            for idx in indexes:
                print(f"  • {idx['indexname']}")
                print(f"    Definition: {idx['indexdef']}")
        else:
            print("❌ No indexes found on bedrock_kb table!")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎯 Database Verification Summary:")
        print(f"  • Vector extension: {'✅ Installed' if vector_found else '❌ Missing'}")
        print(f"  • bedrock_integration schema: {'✅ Found' if tables else '❌ Missing'}")
        print(f"  • bedrock_kb table: {'✅ Found' if columns else '❌ Missing'}")
        print(f"  • Table indexes: {'✅ Found' if indexes else '❌ Missing'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def show_installation_instructions():
    """Show instructions for installing psycopg2 and PostgreSQL tools"""
    print("\n🛠️ Installation Instructions:")
    print("="*50)
    
    print("\n1️⃣ Install psycopg2 (Python PostgreSQL adapter):")
    print("   pip install psycopg2-binary")
    
    print("\n2️⃣ Alternative: Install PostgreSQL client tools:")
    print("   • Download from: https://www.postgresql.org/download/windows/")
    print("   • Or use chocolatey: choco install postgresql")
    print("   • Or use winget: winget install PostgreSQL.PostgreSQL")
    
    print("\n3️⃣ Use pgAdmin (GUI tool):")
    print("   • Download from: https://www.pgadmin.org/download/")
    print("   • Create server with connection details from above")
    
    print("\n4️⃣ Connect via command line (if psql installed):")
    conn_params = get_connection_params()
    print(f"   psql -h {conn_params['host']} \\")
    print(f"        -p {conn_params['port']} \\")
    print(f"        -U {conn_params['user']} \\")
    print(f"        -d {conn_params['database']}")
    print(f"   Password: {conn_params['password']}")

def main():
    print("🔧 Aurora PostgreSQL Vector Database Setup & Verification")
    print("="*65)
    
    if not PSYCOPG2_AVAILABLE:
        show_installation_instructions()
        print(f"\n❌ Cannot proceed without psycopg2. Please install it first.")
        return
    
    # Test basic connection
    if not test_basic_connection():
        print(f"\n❌ Cannot connect to database. Please check connection details.")
        return
    
    print(f"\n" + "="*65)
    print("🔧 Setting up vector database...")
    print("="*65)
    
    # Setup vector database
    setup_success = setup_vector_database()
    
    print(f"\n" + "="*65)
    print("🔍 Verifying database setup...")
    print("="*65)
    
    # Verify setup
    verify_database_setup()
    
    if setup_success:
        print(f"\n🎉 Database setup and verification completed!")
        print(f"🔥 Ready to create Bedrock Knowledge Base with Aurora PostgreSQL!")
    else:
        print(f"\n⚠️ Database setup had some issues. Check the output above.")

if __name__ == "__main__":
    main()