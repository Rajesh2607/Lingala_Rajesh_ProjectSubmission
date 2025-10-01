#!/usr/bin/env python3
"""
Automated Knowledge Base Creation Script
Creates a Knowledge Base with your uploaded documents
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_knowledge_base():
    """Create a new Knowledge Base"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # Knowledge Base configuration
        kb_config = {
            'name': 'Heavy Machinery Specifications KB',
            'description': 'Knowledge Base for heavy machinery PDF specifications including bulldozer, dump truck, excavator, forklift, and mobile crane',
            'roleArn': 'arn:aws:iam::133720367604:role/AmazonBedrockExecutionRoleForKnowledgeBase_auto_kb',
            'knowledgeBaseConfiguration': {
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v1'
                }
            },
            'storageConfiguration': {
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    'collectionArn': 'arn:aws:aoss:us-west-2:133720367604:collection/bedrock-knowledge-base-collection',
                    'vectorIndexName': 'bedrock-knowledge-base-index',
                    'fieldMapping': {
                        'vectorField': 'vector',
                        'textField': 'text',
                        'metadataField': 'text-metadata'
                    }
                }
            }
        }
        
        print("🔨 Creating Knowledge Base...")
        response = bedrock_agent.create_knowledge_base(**kb_config)
        
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Knowledge Base created with ID: {kb_id}")
        
        return kb_id
        
    except ClientError as e:
        print(f"❌ Error creating Knowledge Base: {e}")
        return None

def create_data_source(kb_id):
    """Create a data source for the Knowledge Base"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        data_source_config = {
            'knowledgeBaseId': kb_id,
            'name': 'Heavy Machinery PDFs',
            'description': 'PDF documents containing heavy machinery specifications',
            'dataSourceConfiguration': {
                's3Configuration': {
                    'bucketArn': 'arn:aws:s3:::bedrock-kb-133720367604',
                    'inclusionPrefixes': ['documents/']
                }
            },
            'vectorIngestionConfiguration': {
                'chunkingConfiguration': {
                    'chunkingStrategy': 'FIXED_SIZE',
                    'fixedSizeChunkingConfiguration': {
                        'maxTokens': 300,
                        'overlapPercentage': 20
                    }
                }
            }
        }
        
        print("📁 Creating data source...")
        response = bedrock_agent.create_data_source(**data_source_config)
        
        data_source_id = response['dataSource']['dataSourceId']
        print(f"✅ Data source created with ID: {data_source_id}")
        
        return data_source_id
        
    except ClientError as e:
        print(f"❌ Error creating data source: {e}")
        return None

def start_ingestion_job(kb_id, data_source_id):
    """Start the document ingestion process"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        print("🚀 Starting document ingestion...")
        response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=data_source_id
        )
        
        job_id = response['ingestionJob']['ingestionJobId']
        print(f"✅ Ingestion job started with ID: {job_id}")
        
        # Monitor the job
        print("⏳ Monitoring ingestion progress...")
        while True:
            job_status = bedrock_agent.get_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id,
                ingestionJobId=job_id
            )
            
            status = job_status['ingestionJob']['status']
            print(f"   Status: {status}")
            
            if status == 'COMPLETE':
                print("✅ Document ingestion completed successfully!")
                break
            elif status == 'FAILED':
                print("❌ Document ingestion failed!")
                break
            else:
                time.sleep(30)  # Wait 30 seconds before checking again
        
        return job_id
        
    except ClientError as e:
        print(f"❌ Error starting ingestion: {e}")
        return None

def create_simple_kb():
    """Create a simplified Knowledge Base setup"""
    print("🤖 Automated Knowledge Base Creation")
    print("=" * 50)
    
    print("\n⚠️  Note: This requires proper IAM roles and OpenSearch Serverless setup.")
    print("Since these are complex to create programmatically, I recommend:")
    print("\n🎯 RECOMMENDED APPROACH:")
    print("1. Go to AWS Console: https://console.aws.amazon.com/bedrock")
    print("2. Navigate to 'Knowledge bases' in the left menu") 
    print("3. Click 'Create knowledge base'")
    print("4. Follow the wizard:")
    print("   - Name: 'Heavy Machinery Specifications'")
    print("   - Data source: Amazon S3")
    print("   - S3 URI: s3://bedrock-kb-133720367604/documents/")
    print("   - Embeddings model: Titan Text Embeddings v1")
    print("   - Vector database: Amazon OpenSearch Serverless (new collection)")
    print("5. Wait for indexing to complete (5-10 minutes)")
    print("6. Copy the Knowledge Base ID and use it in your Streamlit app")
    
    print(f"\n📋 Your S3 bucket details:")
    print(f"   Bucket: bedrock-kb-133720367604")
    print(f"   Documents: documents/ folder")
    print(f"   Files: 5 PDF specification sheets")

def main():
    create_simple_kb()

if __name__ == "__main__":
    main()