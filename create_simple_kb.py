#!/usr/bin/env python3
"""
Simple Bedrock Knowledge Base Creation
Uses Amazon Bedrock's managed vector database (no OpenSearch required)
"""

import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError

def create_knowledge_base():
    """Create Knowledge Base with managed vector storage"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # First, create IAM role
        iam = boto3.client('iam', region_name='us-west-2')
        role_name = "BedrockKnowledgeBaseRole"
        
        # Trust policy for Bedrock
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
        
        # Permission policy for S3 access
        permission_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::bedrock-kb-133720367604",
                        "arn:aws:s3:::bedrock-kb-133720367604/*"
                    ]
                }
            ]
        }
        
        try:
            # Check if role exists
            role_response = iam.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"✅ Using existing IAM role: {role_arn}")
        except ClientError:
            # Create role
            print("Creating IAM role...")
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for Bedrock Knowledge Base to access S3"
            )
            role_arn = role_response['Role']['Arn']
            
            # Create and attach inline policy
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName="BedrockS3Access",
                PolicyDocument=json.dumps(permission_policy)
            )
            
            print(f"✅ Created IAM role: {role_arn}")
            print("Waiting for role to propagate...")
            time.sleep(30)
        
        # Create Knowledge Base with managed vector storage
        print("Creating Knowledge Base...")
        kb_response = bedrock_agent.create_knowledge_base(
            name="Heavy-Machinery-KB",
            description="Knowledge Base for heavy machinery specifications",
            roleArn=role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v1'
                }
            },
            storageConfiguration={
                'type': 'PINECONE',
                'pineconeConfiguration': {
                    'connectionString': 'https://dummy-connection-string.com',
                    'credentialsSecretArn': 'arn:aws:secretsmanager:us-west-2:133720367604:secret:dummy',
                    'namespace': 'heavy-machinery',
                    'fieldMapping': {
                        'textField': 'text',
                        'metadataField': 'metadata'
                    }
                }
            }
        )
        
        kb_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Created Knowledge Base: {kb_id}")
        return kb_id, role_arn
        
    except ClientError as e:
        print(f"❌ Error: {e}")
        return None, None

def create_with_simple_approach():
    """Try creating KB with simpler configuration"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # Simplified approach - let's try to use existing resources if any
        print("🚀 Creating Bedrock Knowledge Base")
        print("Using S3 bucket: bedrock-kb-133720367604")
        print("Documents path: documents/")
        
        # First let's see what foundation models are available
        bedrock = boto3.client('bedrock', region_name='us-west-2')
        models = bedrock.list_foundation_models()
        
        # Find Titan embedding model
        titan_models = [m for m in models['modelSummaries'] if 'titan-embed' in m['modelId']]
        if titan_models:
            embedding_model = titan_models[0]['modelArn']
            print(f"✅ Found embedding model: {embedding_model}")
        else:
            print("❌ No Titan embedding models found")
            return None
        
        return embedding_model
        
    except ClientError as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🧠 Simple Bedrock Knowledge Base Creator")
    print("=" * 50)
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts', region_name='us-west-2')
        account = sts.get_caller_identity()['Account']
        print(f"✅ AWS Account: {account}")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return
    
    # Check S3 documents
    try:
        s3 = boto3.client('s3', region_name='us-west-2')
        response = s3.list_objects_v2(Bucket='bedrock-kb-133720367604', Prefix='documents/')
        
        if 'Contents' in response:
            pdf_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.pdf')]
            print(f"✅ Found {len(pdf_files)} PDF documents:")
            for pdf in pdf_files:
                print(f"   - {pdf}")
        else:
            print("❌ No documents found in S3")
            return
            
    except ClientError as e:
        print(f"❌ S3 error: {e}")
        return
    
    # Show manual creation instructions
    print("\n" + "=" * 60)
    print("📋 MANUAL KNOWLEDGE BASE CREATION GUIDE")
    print("=" * 60)
    print()
    print("Since automated creation requires specific permissions and configurations,")
    print("here are the steps to create the Knowledge Base manually in AWS Console:")
    print()
    print("1. 🌐 Open AWS Console → Amazon Bedrock")
    print("2. 📚 Navigate to 'Knowledge bases' in the left menu")
    print("3. ➕ Click 'Create knowledge base'")
    print()
    print("4. 📝 Knowledge Base Details:")
    print("   - Name: Heavy-Machinery-KB")
    print("   - Description: Knowledge Base for heavy machinery specifications")
    print()
    print("5. 🔐 IAM Permissions:")
    print("   - Choose 'Create and use a new service role'")
    print("   - Or use existing role with S3 permissions")
    print()
    print("6. 📊 Data Source Configuration:")
    print("   - Data source type: Amazon S3")
    print(f"   - S3 URI: s3://bedrock-kb-133720367604/documents/")
    print("   - Chunking: Default chunking")
    print()
    print("7. 🧮 Embeddings Model:")
    print("   - Select: Titan Embeddings G1 - Text")
    print("   - Vector database: Quick create a new vector store")
    print()
    print("8. ✅ Review and Create")
    print()
    print("9. 📋 After creation, note down the Knowledge Base ID")
    print("   and update your Streamlit app configuration.")
    print()
    print("💡 Expected documents to be processed:")
    for pdf in pdf_files:
        print(f"   ✓ {pdf}")
    
    # Try to get existing knowledge bases
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        kb_list = bedrock_agent.list_knowledge_bases()
        
        if kb_list['knowledgeBaseSummaries']:
            print("\n" + "=" * 50)
            print("📚 EXISTING KNOWLEDGE BASES FOUND:")
            print("=" * 50)
            for kb in kb_list['knowledgeBaseSummaries']:
                print(f"   📚 {kb['name']}")
                print(f"      ID: {kb['knowledgeBaseId']}")
                print(f"      Status: {kb['status']}")
                print(f"      Updated: {kb.get('updatedAt', 'N/A')}")
                print()
                
                # Save KB info for easy access
                kb_info = {
                    'knowledge_base_id': kb['knowledgeBaseId'],
                    'name': kb['name'],
                    'status': kb['status'],
                    'region': 'us-west-2',
                    'account': account
                }
                
                with open(f"kb_{kb['knowledgeBaseId']}.json", 'w') as f:
                    json.dump(kb_info, f, indent=2, default=str)
                
                print(f"💾 KB info saved to: kb_{kb['knowledgeBaseId']}.json")
        else:
            print("\n❌ No existing Knowledge Bases found")
            
    except ClientError as e:
        print(f"\n❌ Error listing Knowledge Bases: {e}")

if __name__ == "__main__":
    main()