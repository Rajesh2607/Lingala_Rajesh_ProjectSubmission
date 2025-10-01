#!/usr/bin/env python3
"""
Alternative Database Connection Methods for Aurora PostgreSQL
Since RDS Data API is not available, let's try alternative approaches
"""

import boto3
import json
from botocore.exceptions import ClientError

def get_connection_details():
    """Get detailed connection information for alternative methods"""
    try:
        # Get database credentials
        secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-1NyjuJ"
        secretsmanager = boto3.client('secretsmanager', region_name='us-west-2')
        response = secretsmanager.get_secret_value(SecretId=secret_arn)
        secret_data = json.loads(response['SecretString'])
        
        # Get RDS cluster information
        rds = boto3.client('rds', region_name='us-west-2')
        clusters = rds.describe_db_clusters(DBClusterIdentifier='my-aurora-serverless')
        cluster_info = clusters['DBClusters'][0]
        
        return {
            'endpoint': cluster_info['Endpoint'],
            'reader_endpoint': cluster_info.get('ReaderEndpoint', ''),
            'port': cluster_info['Port'],
            'database': secret_data.get('db', 'myapp'),
            'username': secret_data.get('username', 'dbadmin'),
            'password': secret_data.get('password'),
            'engine_version': cluster_info['EngineVersion'],
            'status': cluster_info['Status']
        }
    except Exception as e:
        print(f"❌ Error getting connection details: {e}")
        return None

def show_alternative_methods(conn_info):
    """Show alternative connection methods"""
    if not conn_info:
        print("❌ Cannot retrieve connection information")
        return
    
    print("🔄 Alternative Database Connection Methods")
    print("=" * 60)
    
    print(f"\n📊 **Database Information:**")
    print(f"   • Endpoint: {conn_info['endpoint']}")
    print(f"   • Port: {conn_info['port']}")
    print(f"   • Database: {conn_info['database']}")
    print(f"   • Username: {conn_info['username']}")
    print(f"   • Password: {conn_info['password']}")
    print(f"   • Engine: PostgreSQL {conn_info['engine_version']}")
    print(f"   • Status: {conn_info['status']}")
    
    print(f"\n1️⃣ **Try RDS Query Editor with Database Credentials (Not Data API):**")
    print("   Instead of using 'Connect using RDS Data API', try:")
    print("   • Click 'Add new database credentials'")
    print("   • Choose 'Connect using database credentials'")
    print("   • Enter the credentials manually (not from Secrets Manager)")
    
    print(f"\n2️⃣ **Connect with psql (Command Line):**")
    print("   If you have PostgreSQL client installed:")
    print(f"   psql -h {conn_info['endpoint']} \\")
    print(f"        -p {conn_info['port']} \\")
    print(f"        -U {conn_info['username']} \\")
    print(f"        -d {conn_info['database']}")
    print(f"   Password: {conn_info['password']}")
    
    print(f"\n3️⃣ **Install psql on Windows:**")
    print("   • Download PostgreSQL tools: https://www.postgresql.org/download/windows/")
    print("   • Or use: winget install PostgreSQL.PostgreSQL")
    print("   • Add to PATH: C:\\Program Files\\PostgreSQL\\16\\bin")
    
    print(f"\n4️⃣ **Use pgAdmin (GUI Tool):**")
    print("   • Download pgAdmin: https://www.pgadmin.org/download/")
    print("   • Create new server connection with above details")
    
    print(f"\n5️⃣ **Python Connection (if psycopg2 available):**")
    print("   • Install: pip install psycopg2-binary")
    print("   • Use direct PostgreSQL connection")

def show_workaround_sql():
    """Show SQL commands that might work with limited permissions"""
    
    print(f"\n🛠️ **Workaround: Simplified Setup Commands**")
    print("=" * 50)
    
    print("Try these simplified commands one by one in RDS Query Editor:")
    print("(These might work with basic database permissions)")
    
    simple_commands = [
        "-- Check current database version",
        "SELECT version();",
        "",
        "-- Check available extensions", 
        "SELECT * FROM pg_available_extensions WHERE name = 'vector';",
        "",
        "-- Try to create extension (may require superuser)",
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "",
        "-- If vector extension fails, check what extensions are available",
        "SELECT * FROM pg_extension;",
        "",
        "-- Create schema (should work with basic permissions)",
        "CREATE SCHEMA IF NOT EXISTS bedrock_integration;",
        "",
        "-- Check if schema was created",
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bedrock_integration';",
    ]
    
    for cmd in simple_commands:
        print(f"   {cmd}")

def main():
    print("🔧 Aurora PostgreSQL Connection Troubleshooting")
    print("=" * 55)
    
    print("\n❌ **Issue Identified:**")
    print("   RDS Data API permissions are not available in AWS Lab environment")
    print("   Error: 'rds-data:ExecuteStatement' action not allowed")
    
    conn_info = get_connection_details()
    show_alternative_methods(conn_info)
    show_workaround_sql()
    
    print(f"\n" + "=" * 60)
    print("🎯 **Recommended Next Steps:**")
    print("=" * 60)
    print("1. Try RDS Query Editor with 'database credentials' (not Data API)")
    print("2. Install PostgreSQL client tools (psql) for direct connection")
    print("3. Use the simplified SQL commands above")
    print("4. Focus on creating Bedrock Knowledge Base with S3 instead of Aurora")
    
    print(f"\n💡 **Alternative Approach:**")
    print("   Since Aurora setup is challenging with current permissions,")
    print("   we can create Bedrock Knowledge Base using:")
    print("   • Amazon OpenSearch Serverless (managed vector store)")
    print("   • Or Pinecone (if available)")
    print("   • S3 documents are already ready for ingestion")

if __name__ == "__main__":
    main()