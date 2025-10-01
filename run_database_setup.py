#!/usr/bin/env python3
"""
Enhanced Database Setup with Better Error Handling and Output Display
"""
import boto3
import json
import time
from botocore.exceptions import ClientError

def execute_sql_with_data_api(sql_statement, cluster_arn, secret_arn):
    """Execute SQL using RDS Data API with detailed output"""
    try:
        rds_client = boto3.client('rds-data', region_name='us-west-2')
        
        print(f"🔄 Executing: {sql_statement}")
        
        response = rds_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database='myapp',
            sql=sql_statement,
            includeResultMetadata=True
        )
        
        print(f"✅ Success!")
        
        # Display results if any
        if 'records' in response and response['records']:
            print(f"📊 Results:")
            records = response['records']
            for i, record in enumerate(records):
                print(f"   Row {i+1}: {record}")
        
        if 'numberOfRecordsUpdated' in response:
            print(f"📈 Records affected: {response['numberOfRecordsUpdated']}")
            
        return True, response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Error ({error_code}): {error_message}")
        return False, str(e)

def try_alternative_connection():
    """Try alternative connection methods"""
    print("\n🔄 Trying alternative approaches...")
    
    # Check if we can at least verify the cluster exists
    try:
        rds = boto3.client('rds', region_name='us-west-2')
        clusters = rds.describe_db_clusters()
        
        aurora_clusters = [c for c in clusters['DBClusters'] if 'aurora' in c['DBClusterIdentifier']]
        
        if aurora_clusters:
            print("✅ Found Aurora clusters:")
            for cluster in aurora_clusters:
                print(f"   - {cluster['DBClusterIdentifier']}")
                print(f"     Status: {cluster['Status']}")
                print(f"     Engine: {cluster['Engine']} {cluster['EngineVersion']}")
                print(f"     Endpoint: {cluster['Endpoint']}")
                print(f"     Port: {cluster['Port']}")
                print(f"     Database: {cluster.get('DatabaseName', 'N/A')}")
        else:
            print("❌ No Aurora clusters found")
            
    except ClientError as e:
        print(f"❌ Cannot access RDS service: {e}")

def show_manual_execution_steps():
    """Show step-by-step manual execution"""
    print("\n" + "="*80)
    print("📋 MANUAL DATABASE SETUP STEPS")
    print("="*80)
    
    print("\n1️⃣ **Access AWS RDS Query Editor:**")
    print("   • Open AWS Console: https://console.aws.amazon.com/rds/")
    print("   • Navigate to: Databases > my-aurora-serverless")
    print("   • Click: 'Query Editor' tab")
    print("   • Connect using database credentials")
    
    print("\n2️⃣ **Run Setup Commands (Copy & Paste):**")
    
    commands = [
        "-- Step 1: Enable vector extension",
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "",
        "-- Step 2: Create schema",
        "CREATE SCHEMA IF NOT EXISTS bedrock_integration;",
        "",
        "-- Step 3: Create user",
        "DO $$ BEGIN CREATE ROLE bedrock_user LOGIN; EXCEPTION WHEN duplicate_object THEN RAISE NOTICE 'Role exists'; END $$;",
        "",
        "-- Step 4: Set permissions",
        "GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;",
        "ALTER ROLE bedrock_user PASSWORD 'BedrockUser2024!';",
        "",
        "-- Step 5: Create vector table",
        "CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (",
        "    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),",
        "    embedding vector(1536),",
        "    chunks text,",
        "    metadata json",
        ");",
        "",
        "-- Step 6: Create indexes",
        "CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);",
        "GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;",
    ]
    
    for cmd in commands:
        print(f"   {cmd}")
    
    print("\n3️⃣ **Verification Queries:**")
    verification_queries = [
        "-- Check if vector extension is installed",
        "SELECT * FROM pg_extension WHERE extname = 'vector';",
        "",
        "-- Check bedrock_integration tables", 
        "SELECT table_schema || '.' || table_name as show_tables",
        "FROM information_schema.tables",
        "WHERE table_type = 'BASE TABLE' AND table_schema = 'bedrock_integration';",
        "",
        "-- Check all extensions",
        "SELECT * FROM pg_extension;",
        "",
        "-- Check database version",
        "SELECT version();"
    ]
    
    for query in verification_queries:
        print(f"   {query}")
    
    print("\n4️⃣ **Expected Results:**")
    print("   • Vector extension should be listed in pg_extension")
    print("   • bedrock_integration.bedrock_kb table should exist")
    print("   • No errors during table/index creation")

def main():
    print("🚀 Enhanced Aurora PostgreSQL Database Setup")
    print("="*60)
    
    # Database connection details
    cluster_arn = "arn:aws:rds:us-west-2:133720367604:cluster:my-aurora-serverless"
    secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-1NyjuJ"
    
    print(f"🎯 Target Aurora Cluster: my-aurora-serverless")
    print(f"🔐 Using Secret: {secret_arn.split('/')[-1]}")
    
    # SQL commands to execute
    setup_commands = [
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "CREATE SCHEMA IF NOT EXISTS bedrock_integration;", 
        "DO $$ BEGIN CREATE ROLE bedrock_user LOGIN; EXCEPTION WHEN duplicate_object THEN RAISE NOTICE 'Role already exists'; END $$;",
        "GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;",
        "ALTER ROLE bedrock_user PASSWORD 'BedrockUser2024!';",
        """CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            embedding vector(1536),
            chunks text,
            metadata json
        );""",
        "CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);",
        "GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;"
    ]
    
    verification_queries = [
        "SELECT * FROM pg_extension WHERE extname = 'vector';",
        "SELECT table_schema || '.' || table_name as show_tables FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema = 'bedrock_integration';"
    ]
    
    print(f"\n📋 Setup Commands ({len(setup_commands)} commands):")
    print("-" * 50)
    
    success_count = 0
    
    # Try to execute setup commands
    for i, cmd in enumerate(setup_commands, 1):
        print(f"\n[{i}/{len(setup_commands)}]", end=" ")
        success, result = execute_sql_with_data_api(cmd, cluster_arn, secret_arn)
        if success:
            success_count += 1
        time.sleep(1)  # Brief pause between commands
    
    print(f"\n📊 Setup Summary: {success_count}/{len(setup_commands)} commands executed successfully")
    
    if success_count > 0:
        print(f"\n🔍 Running Verification Queries:")
        print("-" * 40)
        
        for i, query in enumerate(verification_queries, 1):
            print(f"\n[Verification {i}]", end=" ")
            success, result = execute_sql_with_data_api(query, cluster_arn, secret_arn)
    else:
        print(f"\n⚠️  Database setup via RDS Data API failed")
        try_alternative_connection()
    
    # Always show manual steps as backup
    show_manual_execution_steps()
    
    print(f"\n" + "="*80)
    print("✅ NEXT STEPS")
    print("="*80)
    print("1. If automated setup failed, use AWS RDS Query Editor (manual steps above)")
    print("2. Run verification queries to confirm setup")
    print("3. Database will be ready for Bedrock Knowledge Base integration")
    print("4. Use Aurora PostgreSQL as vector store for Knowledge Base")

if __name__ == "__main__":
    main()