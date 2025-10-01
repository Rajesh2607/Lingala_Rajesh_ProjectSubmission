#!/usr/bin/env python3
"""
Aurora PostgreSQL Vector Database Configuration Script
Provides SQL commands to set up vector storage for Bedrock Knowledge Base
"""

import boto3
import json
from botocore.exceptions import ClientError

def get_database_connection_info():
    """Get database connection information from Terraform outputs and Secrets Manager"""
    try:
        # Get database endpoint from Stack 1
        print("🔍 Getting database connection information...")
        
        # Database endpoint
        db_endpoint = "my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com"
        secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-1NyjuJ"
        
        # Get database credentials from Secrets Manager
        try:
            secretsmanager = boto3.client('secretsmanager', region_name='us-west-2')
            secret_response = secretsmanager.get_secret_value(SecretId=secret_arn)
            secret_data = json.loads(secret_response['SecretString'])
            
            print("✅ Database connection information retrieved:")
            print(f"   Endpoint: {db_endpoint}")
            print(f"   Database: {secret_data.get('db', 'myapp')}")
            print(f"   Username: {secret_data.get('username', 'dbadmin')}")
            print(f"   Port: {secret_data.get('port', 5432)}")
            
            return {
                'endpoint': db_endpoint,
                'database': secret_data.get('db', 'myapp'),
                'username': secret_data.get('username', 'dbadmin'),
                'password': secret_data.get('password'),
                'port': secret_data.get('port', 5432)
            }
            
        except ClientError as e:
            print(f"❌ Cannot access secrets manager: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting connection info: {e}")
        return None

def generate_sql_commands():
    """Generate SQL commands for vector database setup"""
    
    sql_commands = [
        "-- Enable the vector extension",
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "",
        "-- Create bedrock_integration schema", 
        "CREATE SCHEMA IF NOT EXISTS bedrock_integration;",
        "",
        "-- Create bedrock_user role",
        "DO $$ BEGIN",
        "    CREATE ROLE bedrock_user LOGIN;",
        "EXCEPTION WHEN duplicate_object THEN",
        "    RAISE NOTICE 'Role bedrock_user already exists';",
        "END $$;",
        "",
        "-- Grant permissions on schema",
        "GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;",
        "",
        "-- Set password for bedrock_user (replace 'your_password' with actual password)",
        "ALTER ROLE bedrock_user PASSWORD 'BedrockUser2024!';",
        "",
        "-- Switch to bedrock_user (optional - can be done in separate session)",
        "-- SET SESSION AUTHORIZATION bedrock_user;",
        "",
        "-- Create the main table for vector storage",
        "CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (",
        "    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),",
        "    embedding vector(1536),",
        "    chunks text,",
        "    metadata json",
        ");",
        "",
        "-- Create vector index for similarity search",
        "CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx ",
        "ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);",
        "",
        "-- Grant permissions on table to bedrock_user",
        "GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;",
        "",
        "-- Create additional indexes for better performance",
        "CREATE INDEX IF NOT EXISTS bedrock_kb_metadata_idx ",
        "ON bedrock_integration.bedrock_kb USING gin (metadata);",
        "",
        "-- Check extensions",
        "SELECT * FROM pg_extension WHERE extname = 'vector';",
        "",
        "-- Check schema and tables",
        "SELECT table_schema || '.' || table_name as show_tables",
        "FROM information_schema.tables",
        "WHERE table_type = 'BASE TABLE'",
        "AND table_schema = 'bedrock_integration';",
        "",
        "-- Check table structure",
        "\\d bedrock_integration.bedrock_kb",
        "",
        "-- Test vector operations (optional)",
        "-- INSERT INTO bedrock_integration.bedrock_kb (embedding, chunks, metadata) ",
        "-- VALUES ('[0.1,0.2,0.3]'::vector, 'test chunk', '{\"source\": \"test\"}'::json);",
        "",
        "-- Check if data was inserted",
        "-- SELECT COUNT(*) FROM bedrock_integration.bedrock_kb;"
    ]
    
    return sql_commands

def provide_connection_methods(conn_info):
    """Provide different methods to connect to the database"""
    
    print("\n" + "=" * 70)
    print("🔗 DATABASE CONNECTION METHODS")
    print("=" * 70)
    
    if conn_info:
        print("\n1️⃣  AWS RDS Query Editor (Recommended for AWS Console)")
        print("   - Go to AWS Console → RDS → Databases")
        print("   - Select 'my-aurora-serverless' cluster")
        print("   - Click 'Query Editor'")
        print("   - Connect using database credentials")
        print(f"   - Database name: {conn_info['database']}")
        print(f"   - Username: {conn_info['username']}")
        
        print("\n2️⃣  psql Command Line")
        print("   If you have psql installed:")
        print(f"   psql -h {conn_info['endpoint']} \\")
        print(f"        -p {conn_info['port']} \\")
        print(f"        -U {conn_info['username']} \\")
        print(f"        -d {conn_info['database']}")
        
        print("\n3️⃣  pgAdmin or other GUI tools")
        print("   Connection parameters:")
        print(f"   - Host: {conn_info['endpoint']}")
        print(f"   - Port: {conn_info['port']}")
        print(f"   - Database: {conn_info['database']}")
        print(f"   - Username: {conn_info['username']}")
        print("   - Password: (from AWS Secrets Manager)")
        
    else:
        print("❌ Could not retrieve connection information")
        print("Please check AWS permissions for Secrets Manager access")

def main():
    print("🐘 Aurora PostgreSQL Vector Database Setup")
    print("=" * 50)
    
    # Get connection information
    conn_info = get_database_connection_info()
    
    # Generate SQL commands
    sql_commands = generate_sql_commands()
    
    # Save SQL commands to file
    sql_file = "setup_vector_database.sql"
    with open(sql_file, 'w') as f:
        f.write('\n'.join(sql_commands))
    
    print(f"\n💾 SQL commands saved to: {sql_file}")
    
    # Display SQL commands
    print("\n" + "=" * 70)
    print("📝 SQL COMMANDS FOR VECTOR DATABASE SETUP")
    print("=" * 70)
    print()
    for command in sql_commands:
        print(command)
    
    # Provide connection methods
    provide_connection_methods(conn_info)
    
    print("\n" + "=" * 70)
    print("✅ NEXT STEPS")
    print("=" * 70)
    print("1. Connect to your Aurora PostgreSQL database using one of the methods above")
    print("2. Execute the SQL commands from setup_vector_database.sql")
    print("3. Verify the setup by running the verification queries")
    print("4. The database will be ready for Bedrock Knowledge Base integration")
    print()
    print("🔍 Key verification queries:")
    print("   SELECT * FROM pg_extension WHERE extname = 'vector';")
    print("   SELECT table_schema || '.' || table_name as show_tables")
    print("   FROM information_schema.tables") 
    print("   WHERE table_type = 'BASE TABLE' AND table_schema = 'bedrock_integration';")

if __name__ == "__main__":
    main()