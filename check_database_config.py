#!/usr/bin/env python3
"""
Check Aurora PostgreSQL database configuration for Bedrock Knowledge Base
"""

import boto3
import json
import psycopg2
from botocore.exceptions import ClientError

def get_database_credentials():
    """Get database credentials from AWS Secrets Manager"""
    try:
        secrets_client = boto3.client('secretsmanager', region_name='us-west-2')
        
        # Get the secret ARN from terraform output
        secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-3yBTSs"
        
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(response['SecretString'])
        
        return {
            'host': secret['host'],
            'port': secret['port'],
            'username': secret['username'],
            'password': secret['password'],
            'dbname': secret['db']  # Note: the field is 'db' not 'dbname'
        }
    except Exception as e:
        print(f"❌ Error getting database credentials: {e}")
        return None

def connect_to_database(db_config):
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['username'],
            password=db_config['password'],
            database=db_config['dbname']
        )
        print("✅ Successfully connected to Aurora PostgreSQL!")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def run_extension_query(conn):
    """Run the pg_extension query"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pg_extension;")
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        print("\n🔌 PostgreSQL Extensions (SELECT * FROM pg_extension;):")
        print("=" * 80)
        
        # Print header
        header = " | ".join(f"{col:15}" for col in columns)
        print(header)
        print("-" * len(header))
        
        # Print results
        for row in results:
            row_str = " | ".join(f"{str(val):15}" for val in row)
            print(row_str)
            
        print(f"\n✅ Found {len(results)} PostgreSQL extensions")
        
        # Check specifically for vector extension
        vector_extensions = [row for row in results if 'vector' in str(row).lower()]
        if vector_extensions:
            print("🎯 Vector extension found - Database ready for vector storage!")
        else:
            print("⚠️  Vector extension not found")
            
        cursor.close()
        return results
        
    except Exception as e:
        print(f"❌ Error running extension query: {e}")
        return None

def run_bedrock_table_query(conn):
    """Run the bedrock_integration table query"""
    try:
        cursor = conn.cursor()
        query = """
        SELECT
            table_schema || '.' || table_name as show_tables
        FROM
            information_schema.tables
        WHERE
            table_type = 'BASE TABLE'
        AND
            table_schema = 'bedrock_integration';
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n🗄️  Bedrock Integration Tables:")
        print("   Query: SELECT table_schema || '.' || table_name as show_tables")
        print("          FROM information_schema.tables")
        print("          WHERE table_type = 'BASE TABLE' AND table_schema = 'bedrock_integration';")
        print("=" * 60)
        
        if results:
            print("   Tables found:")
            for row in results:
                print(f"   📋 {row[0]}")
            print(f"\n✅ Found {len(results)} bedrock_integration tables")
        else:
            print("   ⚠️  No bedrock_integration tables found")
            print("   💡 This is normal if Knowledge Base hasn't created tables yet")
        
        cursor.close()
        return results
        
    except Exception as e:
        print(f"❌ Error running bedrock table query: {e}")
        return None

def check_database_info(conn):
    """Get basic database information"""
    try:
        cursor = conn.cursor()
        
        # Get PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n📊 Database Information:")
        print(f"   PostgreSQL Version: {version.split(',')[0]}")
        
        # Get database name and size
        cursor.execute("SELECT current_database(), pg_size_pretty(pg_database_size(current_database()));")
        db_info = cursor.fetchone()
        print(f"   Database: {db_info[0]}")
        print(f"   Size: {db_info[1]}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error getting database info: {e}")

def main():
    """Main function to check database configuration"""
    print("🗄️  Aurora PostgreSQL Database Configuration Check")
    print("=" * 60)
    
    # Get database credentials
    print("1. Getting database credentials from Secrets Manager...")
    db_config = get_database_credentials()
    
    if not db_config:
        print("❌ Could not retrieve database credentials")
        return
    
    print(f"   Database Host: {db_config['host']}")
    print(f"   Database Name: {db_config['dbname']}")
    print(f"   Username: {db_config['username']}")
    
    # Connect to database
    print("\n2. Connecting to Aurora PostgreSQL...")
    conn = connect_to_database(db_config)
    
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        # Get database info
        check_database_info(conn)
        
        # Run extension query (REQUIRED QUERY 1)
        print("\n3. Running REQUIRED QUERY 1:")
        extensions = run_extension_query(conn)
        
        # Run bedrock table query (REQUIRED QUERY 2)
        print("\n4. Running REQUIRED QUERY 2:")
        tables = run_bedrock_table_query(conn)
        
        print(f"\n📸 SCREENSHOT RESULTS:")
        print(f"   ✅ Query 1 (SELECT * FROM pg_extension): {len(extensions) if extensions else 0} extensions found")
        print(f"   ✅ Query 2 (bedrock_integration tables): {len(tables) if tables else 0} tables found")
        
    finally:
        conn.close()
        print("\n🎉 Database configuration check complete!")
        print("📸 Take screenshots of the query results above for your documentation!")

if __name__ == "__main__":
    main()