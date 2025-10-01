#!/usr/bin/env python3
"""
List all Knowledge Bases in the account
"""

import boto3
import json
from botocore.exceptions import ClientError

def list_knowledge_bases():
    """List all Knowledge Bases in the account"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        response = bedrock_agent.list_knowledge_bases()
        knowledge_bases = response.get('knowledgeBaseSummaries', [])
        
        print(f"📚 Found {len(knowledge_bases)} Knowledge Bases in us-west-2:")
        print("=" * 60)
        
        if knowledge_bases:
            for i, kb in enumerate(knowledge_bases, 1):
                print(f"{i}. Knowledge Base ID: {kb['knowledgeBaseId']}")
                print(f"   Name: {kb['name']}")
                print(f"   Description: {kb.get('description', 'N/A')}")
                print(f"   Status: {kb['status']}")
                print(f"   Created: {kb.get('createdAt', 'N/A')}")
                print(f"   Updated: {kb.get('updatedAt', 'N/A')}")
                print("-" * 40)
        else:
            print("❌ No Knowledge Bases found in your account.")
            print("\n💡 To create a Knowledge Base:")
            print("   1. Go to AWS Console > Amazon Bedrock")
            print("   2. Navigate to 'Knowledge bases' in the left menu")
            print("   3. Click 'Create knowledge base'")
            print("   4. Use your S3 bucket: bedrock-kb-133720367604")
            print("   5. Point to the documents/ folder with your PDFs")
        
        return knowledge_bases
        
    except ClientError as e:
        print(f"❌ Error listing Knowledge Bases: {e}")
        return []

def check_s3_documents():
    """Check if documents are still in S3"""
    try:
        s3 = boto3.client('s3', region_name='us-west-2')
        
        response = s3.list_objects_v2(
            Bucket='bedrock-kb-133720367604',
            Prefix='documents/'
        )
        
        objects = response.get('Contents', [])
        print(f"\n📁 Found {len(objects)} documents in S3:")
        
        for obj in objects:
            print(f"   - {obj['Key']} ({obj['Size']} bytes)")
            
        return len(objects) > 0
        
    except ClientError as e:
        print(f"❌ Error checking S3: {e}")
        return False

def main():
    print("🔍 Knowledge Base Discovery")
    print("=" * 40)
    
    # List existing Knowledge Bases
    kbs = list_knowledge_bases()
    
    # Check S3 documents
    check_s3_documents()
    
    print("\n🚀 Next Steps:")
    if not kbs:
        print("   1. Create a new Knowledge Base in AWS Console")
        print("   2. Use S3 bucket: bedrock-kb-133720367604")
        print("   3. Set data source to documents/ folder")
        print("   4. Wait for indexing to complete")
        print("   5. Use the new KB ID in your Streamlit app")
    else:
        print("   1. Use one of the existing Knowledge Base IDs above")
        print("   2. Update your Streamlit app with the correct ID")

if __name__ == "__main__":
    main()