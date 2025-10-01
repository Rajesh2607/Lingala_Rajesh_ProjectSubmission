#!/usr/bin/env python3
"""
Amazon Bedrock Knowledge Base Creation Script
Creates a Knowledge Base using the uploaded PDF documents in S3
"""

import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

# Configuration
KB_NAME = "heavy-machinery-knowledge-base"
KB_DESCRIPTION = "Knowledge Base for heavy machinery equipment specifications and maintenance"
S3_BUCKET = "bedrock-kb-133720367604"
S3_PREFIX = "documents/"
EMBEDDING_MODEL = "amazon.titan-embed-text-v1"
REGION = "us-west-2"

def check_aws_credentials():
    """Check if AWS credentials are properly configured"""
    try:
        sts = boto3.client('sts', region_name=REGION)
        response = sts.get_caller_identity()
        account_id = response['Account']
        print(f"✅ AWS credentials configured for account: {account_id}")
        return account_id
    except (NoCredentialsError, ClientError) as e:
        print(f"❌ AWS credential error: {e}")
        return None

def check_bedrock_access():
    """Check if Bedrock service is accessible"""
    try:
        bedrock = boto3.client('bedrock', region_name=REGION)
        # Try to list foundation models to test access
        response = bedrock.list_foundation_models()
        print(f"✅ Bedrock access confirmed - Found {len(response['modelSummaries'])} models")
        return True
    except ClientError as e:
        print(f"❌ Bedrock access error: {e}")
        return False

def check_s3_documents():
    """Check if the PDF documents exist in S3"""
    try:
        s3 = boto3.client('s3', region_name=REGION)
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
        
        if 'Contents' not in response:
            print(f"❌ No documents found in s3://{S3_BUCKET}/{S3_PREFIX}")
            return False
            
        pdf_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
        print(f"✅ Found {len(pdf_files)} PDF documents in S3:")
        for pdf in pdf_files:
            print(f"   - {pdf}")
        return pdf_files
    except ClientError as e:
        print(f"❌ S3 access error: {e}")
        return False

def create_opensearch_serverless_collection():
    """Create OpenSearch Serverless collection for vector storage"""
    try:
        opensearch = boto3.client('opensearchserverless', region_name=REGION)
        
        collection_name = f"{KB_NAME}-collection".replace("_", "-")
        
        # Check if collection already exists
        try:
            response = opensearch.batch_get_collection(names=[collection_name])
            if response['collectionDetails']:
                print(f"✅ OpenSearch collection '{collection_name}' already exists")
                return response['collectionDetails'][0]['id']
        except ClientError:
            pass
        
        # Create collection
        print(f"Creating OpenSearch Serverless collection: {collection_name}")
        response = opensearch.create_collection(
            name=collection_name,
            type='VECTORSEARCH',
            description=f"Vector collection for {KB_DESCRIPTION}"
        )
        
        collection_id = response['createCollectionDetail']['id']
        print(f"✅ Created OpenSearch collection: {collection_id}")
        
        # Wait for collection to be active
        print("Waiting for collection to become active...")
        while True:
            status_response = opensearch.batch_get_collection(ids=[collection_id])
            status = status_response['collectionDetails'][0]['status']
            if status == 'ACTIVE':
                break
            elif status == 'FAILED':
                raise Exception("Collection creation failed")
            time.sleep(10)
            print("Still creating...")
        
        print("✅ OpenSearch collection is now active")
        return collection_id
        
    except ClientError as e:
        print(f"❌ Error creating OpenSearch collection: {e}")
        return None

def create_knowledge_base(account_id, collection_id):
    """Create the Bedrock Knowledge Base"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
        
        # Create IAM role for Knowledge Base
        iam = boto3.client('iam', region_name=REGION)
        role_name = f"{KB_NAME}-role"
        
        try:
            # Try to get existing role
            role_response = iam.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"✅ Using existing IAM role: {role_arn}")
        except ClientError:
            # Create new role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "bedrock.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Role for {KB_DESCRIPTION}"
            )
            role_arn = role_response['Role']['Arn']
            
            # Attach policies
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            )
            
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
            )
            
            print(f"✅ Created IAM role: {role_arn}")
            
            # Wait a bit for role to propagate
            print("Waiting for IAM role to propagate...")
            time.sleep(30)
        
        # Create Knowledge Base
        print("Creating Bedrock Knowledge Base...")
        kb_response = bedrock_agent.create_knowledge_base(
            name=KB_NAME,
            description=KB_DESCRIPTION,
            roleArn=role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': f'arn:aws:bedrock:{REGION}::foundation-model/{EMBEDDING_MODEL}'
                }
            },
            storageConfiguration={
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    'collectionArn': f'arn:aws:aoss:{REGION}:{account_id}:collection/{collection_id}',
                    'vectorIndexName': 'heavy-machinery-index',
                    'fieldMapping': {
                        'vectorField': 'vector',
                        'textField': 'text',
                        'metadataField': 'metadata'
                    }
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Created Knowledge Base: {kb_id}")
        
        # Create Data Source
        print("Creating data source...")
        ds_response = bedrock_agent.create_data_source(
            knowledgeBaseId=kb_id,
            name=f"{KB_NAME}-s3-source",
            description="S3 data source for heavy machinery PDFs",
            dataSourceConfiguration={
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::{S3_BUCKET}',
                    'inclusionPrefixes': [S3_PREFIX]
                }
            }
        )
        
        ds_id = ds_response['dataSource']['dataSourceId']
        print(f"✅ Created data source: {ds_id}")
        
        # Start ingestion job
        print("Starting document ingestion...")
        job_response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id,
            description="Initial ingestion of heavy machinery PDFs"
        )
        
        job_id = job_response['ingestionJob']['ingestionJobId']
        print(f"✅ Started ingestion job: {job_id}")
        
        return kb_id, ds_id, job_id
        
    except ClientError as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        return None, None, None

def main():
    """Main function to create the Knowledge Base"""
    print("🚀 Amazon Bedrock Knowledge Base Creation")
    print("=" * 50)
    
    # Check prerequisites
    account_id = check_aws_credentials()
    if not account_id:
        print("❌ Please configure valid AWS credentials")
        return
    
    if not check_bedrock_access():
        print("❌ Cannot access Bedrock service")
        return
    
    pdf_files = check_s3_documents()
    if not pdf_files:
        print("❌ No PDF documents found in S3")
        return
    
    print(f"\n📊 Summary:")
    print(f"   Account: {account_id}")
    print(f"   Region: {REGION}")
    print(f"   S3 Bucket: {S3_BUCKET}")
    print(f"   Documents: {len(pdf_files)} PDFs")
    
    # Create OpenSearch collection
    print(f"\n🔍 Creating OpenSearch Serverless collection...")
    collection_id = create_opensearch_serverless_collection()
    if not collection_id:
        print("❌ Failed to create OpenSearch collection")
        return
    
    # Create Knowledge Base
    print(f"\n🧠 Creating Bedrock Knowledge Base...")
    kb_id, ds_id, job_id = create_knowledge_base(account_id, collection_id)
    
    if kb_id:
        print(f"\n🎉 Success! Knowledge Base created:")
        print(f"   Knowledge Base ID: {kb_id}")
        print(f"   Data Source ID: {ds_id}")
        print(f"   Ingestion Job ID: {job_id}")
        print(f"\n📝 Update your Streamlit app with this Knowledge Base ID:")
        print(f"   kb_id = '{kb_id}'")
        
        # Save to file for easy reference
        with open('knowledge_base_info.json', 'w') as f:
            json.dump({
                'knowledge_base_id': kb_id,
                'data_source_id': ds_id,
                'ingestion_job_id': job_id,
                'collection_id': collection_id,
                'created_at': datetime.now().isoformat(),
                'account_id': account_id,
                'region': REGION
            }, f, indent=2)
        
        print(f"\n💾 Knowledge Base details saved to: knowledge_base_info.json")
    else:
        print("❌ Failed to create Knowledge Base")

if __name__ == "__main__":
    main()