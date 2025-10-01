#!/usr/bin/env python3
"""
Test the new Knowledge Base L3CRT5Q79H
"""

import boto3
import json
from botocore.exceptions import ClientError

def test_knowledge_base(kb_id):
    """Test the Knowledge Base functionality"""
    print(f'🧪 Testing Knowledge Base: {kb_id}')
    print('=' * 50)
    
    try:
        # Test Knowledge Base status
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        response = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        kb_info = response['knowledgeBase']
        
        print(f'✅ Knowledge Base Found!')
        print(f'   Name: {kb_info["name"]}')
        print(f'   Status: {kb_info["status"]}')
        print(f'   Description: {kb_info.get("description", "N/A")}')
        
        # Check data sources
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        print(f'   Data Sources: {len(data_sources["dataSourceSummaries"])}')
        
        for ds in data_sources["dataSourceSummaries"]:
            print(f'     - {ds["name"]}: {ds["status"]}')
        
        # Test retrieval
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        test_queries = [
            'BD850 bulldozer engine specifications',
            'DT1000 dump truck payload capacity',
            'X950 excavator digging depth'
        ]
        
        print(f'\n🔍 Testing Document Retrieval:')
        for query in test_queries:
            print(f'\n   Query: "{query}"')
            
            try:
                response = bedrock_runtime.retrieve(
                    knowledgeBaseId=kb_id,
                    retrievalQuery={'text': query},
                    retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 2}}
                )
                
                results = response['retrievalResults']
                print(f'   ✅ Retrieved {len(results)} results')
                
                for i, result in enumerate(results, 1):
                    print(f'     Result {i}: Score {result["score"]:.3f}')
                    print(f'     Content: {result["content"]["text"][:80]}...')
                    if 'location' in result and 's3Location' in result['location']:
                        source = result['location']['s3Location']['uri'].split('/')[-1]
                        print(f'     Source: {source}')
                        
            except ClientError as e:
                print(f'   ❌ Retrieval error: {e}')
        
        # Test generation
        print(f'\n🤖 Testing Knowledge Base Generation:')
        test_question = "What are the engine specifications of the BD850 bulldozer?"
        
        try:
            response = bedrock_runtime.retrieve_and_generate(
                input={'text': test_question},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': kb_id,
                        'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
                    }
                }
            )
            
            print(f'   ✅ Generated Response:')
            print(f'   {response["output"]["text"][:200]}...')
            
            if 'citations' in response:
                print(f'   📚 Citations: {len(response["citations"])}')
                
        except ClientError as e:
            print(f'   ❌ Generation error: {e}')
        
        return True
        
    except ClientError as e:
        print(f'❌ Knowledge Base access error: {e}')
        return False

def main():
    kb_id = 'L3CRT5Q79H'
    
    if test_knowledge_base(kb_id):
        print(f'\n🎉 Knowledge Base {kb_id} is working!')
        print(f'\n📝 Ready to use in your Streamlit app at:')
        print(f'   http://localhost:8503')
        print(f'\n💡 Enter KB ID "{kb_id}" in the sidebar and start asking questions!')
    else:
        print(f'\n❌ Knowledge Base {kb_id} needs more time to index.')
        print(f'   Please wait a few more minutes and try again.')

if __name__ == "__main__":
    main()