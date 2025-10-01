#!/usr/bin/env python3
"""
Get Aurora Database Password from AWS Secrets Manager
"""
import boto3
import json
from botocore.exceptions import ClientError

def get_database_password():
    """Retrieve the database password from AWS Secrets Manager"""
    try:
        secret_arn = "arn:aws:secretsmanager:us-west-2:133720367604:secret:my-aurora-serverless-1NyjuJ"
        
        print("🔐 Retrieving Aurora database password from AWS Secrets Manager...")
        print(f"Secret ARN: {secret_arn}")
        
        secretsmanager = boto3.client('secretsmanager', region_name='us-west-2')
        response = secretsmanager.get_secret_value(SecretId=secret_arn)
        
        secret_data = json.loads(response['SecretString'])
        
        print("\n✅ Database credentials retrieved successfully!")
        print("=" * 50)
        print(f"🏷️  Database: {secret_data.get('db', 'myapp')}")
        print(f"👤 Username: {secret_data.get('username', 'dbadmin')}")
        print(f"🌐 Host: {secret_data.get('host', 'my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com')}")
        print(f"🔌 Port: {secret_data.get('port', 5432)}")
        print(f"🔑 Password: {secret_data.get('password', 'Not found')}")
        
        print("\n📋 For AWS RDS Query Editor:")
        print("=" * 30)
        print(f"Database instance: my-aurora-serverless")
        print(f"Database username: {secret_data.get('username', 'dbadmin')}")
        print(f"Database password: {secret_data.get('password', 'Not found')}")
        print(f"Database name: {secret_data.get('db', 'myapp')}")
        
        return secret_data
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Error accessing AWS Secrets Manager ({error_code}): {error_message}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def main():
    print("🔓 Aurora PostgreSQL Database Password Retrieval")
    print("=" * 55)
    
    credentials = get_database_password()
    
    if credentials:
        print("\n🎯 Connection Steps:")
        print("1. Use the password shown above in the RDS Query Editor")
        print("2. Click 'Connect to database'")
        print("3. Once connected, you can run the vector database setup commands")
        
        print("\n🛠️  Next: Run these setup commands in the Query Editor:")
        print("CREATE EXTENSION IF NOT EXISTS vector;")
        print("CREATE SCHEMA IF NOT EXISTS bedrock_integration;")
        print("-- (and the other commands from setup_vector_database.sql)")
    else:
        print("\n❌ Could not retrieve database password")
        print("Please check AWS credentials and try again")

if __name__ == "__main__":
    main()