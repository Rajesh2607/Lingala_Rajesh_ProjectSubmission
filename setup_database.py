#!/usr/bin/env python3
"""
Script to set up the Aurora database schema for Bedrock Knowledge Base
"""
import boto3
import json
import time

def execute_sql_statement(rds_client, cluster_arn, secret_arn, sql_statement):
    """Execute a SQL statement using RDS Data API"""
    print(f"Executing: {sql_statement}")
    
    response = rds_client.execute_statement(
        resourceArn=cluster_arn,
        secretArn=secret_arn,
        database='myapp',
        sql=sql_statement
    )
    print(f"Response: {response.get('numberOfRecordsUpdated', 0)} records affected")
    return response

def main():
    # AWS configuration from terraform outputs
    cluster_arn = "arn:aws:rds:us-west-2:133720367604:cluster:my-aurora-serverless"
    secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-D8pFMK"
    
    # Initialize RDS Data client
    rds_client = boto3.client('rds-data', region_name='us-west-2')
    
    # SQL statements to create the database schema
    sql_statements = [
        "CREATE EXTENSION IF NOT EXISTS vector;",
        "CREATE SCHEMA IF NOT EXISTS bedrock_integration;",
        "DO $$ BEGIN CREATE ROLE bedrock_user LOGIN; EXCEPTION WHEN duplicate_object THEN RAISE NOTICE 'Role already exists'; END $$;",
        "GRANT ALL ON SCHEMA bedrock_integration to bedrock_user;",
        "SET SESSION AUTHORIZATION bedrock_user;",
        """
        CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
            id uuid PRIMARY KEY,
            embedding vector(1536),
            chunks text,
            metadata json
        );
        """,
        "CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);"
    ]
    
    print("Setting up Aurora database schema for Bedrock Knowledge Base...")
    
    for sql in sql_statements:
        try:
            execute_sql_statement(rds_client, cluster_arn, secret_arn, sql.strip())
            time.sleep(1)  # Small delay between statements
        except Exception as e:
            print(f"Error executing SQL: {e}")
            print(f"SQL was: {sql}")
            if "duplicate_object" not in str(e) and "already exists" not in str(e):
                raise
    
    print("Database schema setup completed successfully!")

if __name__ == "__main__":
    main()