#!/usr/bin/env python3
"""
Test script to validate Knowledge Base functionality
"""

import boto3
import json
from botocore.exceptions import ClientError

def test_knowledge_base_status(kb_id):
    """Test Knowledge Base status and configuration"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # Get Knowledge Base details
        response = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        kb_info = response['knowledgeBase']
        
        print(f"✅ Knowledge Base Status: {kb_info['status']}")
        print(f"   Name: {kb_info['name']}")
        print(f"   Description: {kb_info.get('description', 'N/A')}")
        print(f"   Created: {kb_info.get('createdAt', 'N/A')}")
        print(f"   Updated: {kb_info.get('updatedAt', 'N/A')}")
        
        # Get data sources
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        print(f"   Data Sources: {len(data_sources['dataSourceSummaries'])}")
        
        for ds in data_sources['dataSourceSummaries']:
            print(f"     - {ds['name']}: {ds['status']}")
            print(f"       Description: {ds.get('description', 'N/A')}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Knowledge Base access error: {e}")
        return False

def test_bedrock_retrieval(kb_id, query):
    """Test Knowledge Base retrieval directly"""
    try:
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5
                }
            }
        )
        
        print(f"✅ Retrieved {len(response['retrievalResults'])} results for: '{query}'")
        
        for i, result in enumerate(response['retrievalResults'], 1):
            print(f"   Result {i}:")
            print(f"     Score: {result['score']:.3f}")
            print(f"     Content: {result['content']['text'][:150]}...")
            if 'location' in result:
                location = result['location']
                if 's3Location' in location:
                    s3_uri = location['s3Location'].get('uri', 'Unknown')
                    print(f"     Source: {s3_uri}")
            print()
        
        return len(response['retrievalResults']) > 0
        
    except ClientError as e:
        print(f"❌ Retrieval error: {e}")
        return False

def test_generate_with_kb(kb_id, query):
    """Test Knowledge Base with generation"""
    try:
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                }
            }
        )
        
        print(f"✅ Generated response for: '{query}'")
        print(f"   Response: {response['output']['text'][:200]}...")
        
        # Show citations
        if 'citations' in response:
            print(f"   Citations: {len(response['citations'])}")
            for i, citation in enumerate(response['citations'], 1):
                if 'retrievedReferences' in citation:
                    for ref in citation['retrievedReferences']:
                        if 'location' in ref:
                            location = ref['location']
                            if 's3Location' in location:
                                print(f"     Citation {i}: {location['s3Location'].get('uri', 'Unknown')}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Generation error: {e}")
        return False

def main():
    kb_id = "CXQC5BHAMH"  # Your Knowledge Base ID
    
    print("🧠 Knowledge Base Diagnostic Test")
    print("=" * 50)
    
    # Test 1: Knowledge Base status
    print("\n1. Testing Knowledge Base Status...")
    if test_knowledge_base_status(kb_id):
        
        # Test 2: Direct retrieval
        print("\n2. Testing Document Retrieval...")
        test_queries = [
            "BD850 bulldozer engine specifications",
            "bulldozer operating weight",
            "DT1000 dump truck payload capacity",
            "X950 excavator digging depth",
            "FL250 forklift lifting capacity",
            "MC750 crane maximum capacity"
        ]
        
        retrieval_success = 0
        for query in test_queries:
            print(f"\n   Testing query: '{query}'")
            if test_bedrock_retrieval(kb_id, query):
                retrieval_success += 1
        
        print(f"\n   Retrieval Success Rate: {retrieval_success}/{len(test_queries)}")
        
        # Test 3: Generation with Knowledge Base
        print("\n3. Testing Knowledge Base Generation...")
        generation_queries = [
            "What are the engine specifications of the BD850 bulldozer?",
            "What is the operating weight of the X950 excavator?"
        ]
        
        for query in generation_queries:
            print(f"\n   Testing generation: '{query}'")
            test_generate_with_kb(kb_id, query)
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()