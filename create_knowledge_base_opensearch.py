#!/usr/bin/env python3
"""
Create Bedrock Knowledge Base with OpenSearch Serverless
This approach avoids the Aurora PostgreSQL permission issues
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

class BedrockKnowledgeBaseCreator:
    def __init__(self):
        self.region = 'us-west-2'
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=self.region)
        self.opensearch_serverless = boto3.client('opensearchserverless', region_name=self.region)
        self.iam = boto3.client('iam', region_name=self.region)
        self.s3 = boto3.client('s3', region_name=self.region)
        
        # Configuration
        self.kb_name = "heavy-machinery-knowledge-base"
        self.collection_name = "heavy-machinery-kb"  # Match the created collection
        self.collection_arn = "arn:aws:aoss:us-west-2:133720367604:collection/yrxx5shz6zuntva2zqlf"
        self.s3_bucket = "my-bedrock-knowledge-base-bucket-udacity"
        self.data_source_name = "heavy-machinery-docs"
        
    def create_iam_roles(self):
        """Create IAM roles for Bedrock Knowledge Base"""
        print("🔧 Creating IAM roles...")
        
        # Knowledge Base service role
        kb_trust_policy = {
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
        
        kb_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:Retrieve",
                        "bedrock:RetrieveAndGenerate"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "aoss:APIAccessAll"
                    ],
                    "Resource": f"arn:aws:aoss:{self.region}:*:collection/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{self.s3_bucket}",
                        f"arn:aws:s3:::{self.s3_bucket}/*"
                    ]
                }
            ]
        }
        
        try:
            # Create Knowledge Base role
            kb_role_name = f"{self.kb_name}-service-role"
            try:
                kb_role_response = self.iam.create_role(
                    RoleName=kb_role_name,
                    AssumeRolePolicyDocument=json.dumps(kb_trust_policy),
                    Description="Service role for Bedrock Knowledge Base"
                )
                kb_role_arn = kb_role_response['Role']['Arn']
                print(f"✅ Created Knowledge Base role: {kb_role_arn}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    kb_role_arn = self.iam.get_role(RoleName=kb_role_name)['Role']['Arn']
                    print(f"ℹ️ Using existing Knowledge Base role: {kb_role_arn}")
                else:
                    raise
            
            # Attach policy to Knowledge Base role
            self.iam.put_role_policy(
                RoleName=kb_role_name,
                PolicyName=f"{self.kb_name}-policy",
                PolicyDocument=json.dumps(kb_policy)
            )
            
            return {
                'kb_role_arn': kb_role_arn
            }
            
        except Exception as e:
            print(f"❌ Error creating IAM roles: {e}")
            return None
    
    def get_existing_collection(self):
        """Get the existing OpenSearch Serverless collection"""
        print("🔧 Using existing OpenSearch Serverless collection...")
        
        try:
            collections = self.opensearch_serverless.list_collections()
            for collection in collections['collectionSummaries']:
                if collection['name'] == self.collection_name:
                    print(f"✅ Found existing collection: {collection['id']}")
                    print(f"   ARN: {collection['arn']}")
                    
                    return {
                        'collection_id': collection['id'],
                        'collection_arn': collection['arn'],
                        'endpoint': collection.get('endpoint', '')
                    }
            
            print(f"❌ Collection {self.collection_name} not found")
            return None
            
        except Exception as e:
            print(f"❌ Error getting existing collection: {e}")
            return None
    
    def create_knowledge_base(self, roles, collection_info):
        """Create Bedrock Knowledge Base"""
        print("🔧 Creating Bedrock Knowledge Base...")
        
        try:
            # Knowledge Base configuration
            kb_config = {
                'name': self.kb_name,
                'description': 'Knowledge base for heavy machinery technical documentation',
                'roleArn': roles['kb_role_arn'],
                'knowledgeBaseConfiguration': {
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': f'arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v1'
                    }
                },
                'storageConfiguration': {
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': collection_info['collection_arn'],
                        'vectorIndexName': 'bedrock-knowledge-base-default-index',
                        'fieldMapping': {
                            'vectorField': 'bedrock-knowledge-base-default-vector',
                            'textField': 'AMAZON_BEDROCK_TEXT_CHUNK',
                            'metadataField': 'AMAZON_BEDROCK_METADATA'
                        }
                    }
                }
            }
            
            # Create Knowledge Base
            kb_response = self.bedrock_agent.create_knowledge_base(**kb_config)
            kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
            kb_arn = kb_response['knowledgeBase']['knowledgeBaseArn']
            
            print(f"✅ Created Knowledge Base: {kb_id}")
            print(f"   ARN: {kb_arn}")
            
            return {
                'kb_id': kb_id,
                'kb_arn': kb_arn
            }
            
        except Exception as e:
            print(f"❌ Error creating Knowledge Base: {e}")
            return None
    
    def create_data_source(self, kb_id, roles):
        """Create data source for S3 bucket"""
        print("🔧 Creating data source...")
        
        try:
            ds_config = {
                'knowledgeBaseId': kb_id,
                'name': self.data_source_name,
                'description': 'Heavy machinery specification documents from S3',
                'dataSourceConfiguration': {
                    's3Configuration': {
                        'bucketArn': f'arn:aws:s3:::{self.s3_bucket}',
                        'inclusionPrefixes': ['spec-sheets/']
                    }
                }
            }
            
            # Create data source
            ds_response = self.bedrock_agent.create_data_source(**ds_config)
            ds_id = ds_response['dataSource']['dataSourceId']
            
            print(f"✅ Created data source: {ds_id}")
            
            return {
                'ds_id': ds_id
            }
            
        except Exception as e:
            print(f"❌ Error creating data source: {e}")
            return None
    
    def start_ingestion(self, kb_id, ds_id):
        """Start ingestion job"""
        print("🔧 Starting ingestion job...")
        
        try:
            ingestion_response = self.bedrock_agent.start_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=ds_id,
                description="Initial ingestion of heavy machinery documents"
            )
            
            job_id = ingestion_response['ingestionJob']['ingestionJobId']
            print(f"✅ Started ingestion job: {job_id}")
            
            # Monitor ingestion job
            print("⏳ Monitoring ingestion progress...")
            while True:
                job_status = self.bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds_id,
                    ingestionJobId=job_id
                )
                
                status = job_status['ingestionJob']['status']
                print(f"   Ingestion status: {status}")
                
                if status == 'COMPLETE':
                    print("✅ Ingestion completed successfully!")
                    break
                elif status == 'FAILED':
                    failure_reasons = job_status['ingestionJob'].get('failureReasons', [])
                    print(f"❌ Ingestion failed: {failure_reasons}")
                    break
                
                time.sleep(30)
            
            return job_id
            
        except Exception as e:
            print(f"❌ Error starting ingestion: {e}")
            return None
    
    def create_complete_knowledge_base(self):
        """Create complete Knowledge Base with OpenSearch Serverless"""
        print("🚀 Creating Bedrock Knowledge Base with OpenSearch Serverless")
        print("=" * 70)
        
        # Step 1: Create IAM roles
        roles = self.create_iam_roles()
        if not roles:
            return False
        
        # Step 2: Get existing OpenSearch collection
        collection_info = self.get_existing_collection()
        if not collection_info:
            return False
        
        # Step 3: Create Knowledge Base
        kb_info = self.create_knowledge_base(roles, collection_info)
        if not kb_info:
            return False
        
        # Step 4: Create data source
        ds_info = self.create_data_source(kb_info['kb_id'], roles)
        if not ds_info:
            return False
        
        # Step 5: Start ingestion
        self.start_ingestion(kb_info['kb_id'], ds_info['ds_id'])
        
        print("\n" + "=" * 70)
        print("🎉 Knowledge Base Creation Summary")
        print("=" * 70)
        print(f"Knowledge Base ID: {kb_info['kb_id']}")
        print(f"Knowledge Base ARN: {kb_info['kb_arn']}")
        print(f"Collection ID: {collection_info['collection_id']}")
        print(f"Data Source ID: {ds_info['ds_id']}")
        print(f"S3 Bucket: {self.s3_bucket}")
        
        # Update the app configuration
        self.update_app_config(kb_info['kb_id'])
        
        return True
    
    def update_app_config(self, kb_id):
        """Update app.py with the new Knowledge Base ID"""
        print("🔧 Updating app.py configuration...")
        
        try:
            # Read current app.py
            with open('app.py', 'r') as f:
                content = f.read()
            
            # Replace Knowledge Base ID
            updated_content = content.replace(
                'KNOWLEDGE_BASE_ID = "YOUR_KB_ID_HERE"',
                f'KNOWLEDGE_BASE_ID = "{kb_id}"'
            )
            
            # Write updated content
            with open('app.py', 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Updated app.py with Knowledge Base ID: {kb_id}")
            
        except Exception as e:
            print(f"⚠️ Could not update app.py automatically: {e}")
            print(f"Please manually update KNOWLEDGE_BASE_ID to: {kb_id}")

def main():
    creator = BedrockKnowledgeBaseCreator()
    success = creator.create_complete_knowledge_base()
    
    if success:
        print("\n🎉 Knowledge Base created successfully!")
        print("🔥 You can now run: streamlit run app.py")
    else:
        print("\n❌ Knowledge Base creation failed. Please check the errors above.")

if __name__ == "__main__":
    main()