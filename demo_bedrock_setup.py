#!/usr/bin/env python3
"""
Simple Bedrock Knowledge Base Demo Script
Creates a mock Knowledge Base configuration for demonstration
"""

import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

def test_bedrock_models():
    """Test access to Bedrock models"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Test Claude 3 Haiku with a simple prompt
        test_prompt = "What is heavy machinery?"
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 100,
                'messages': [
                    {
                        'role': 'user',
                        'content': test_prompt
                    }
                ]
            })
        )
        
        result = json.loads(response['body'].read())
        print("✅ Bedrock Claude 3 model access confirmed!")
        print(f"Response: {result['content'][0]['text'][:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock model access error: {e}")
        return False

def create_demo_kb_config():
    """Create a demo Knowledge Base configuration"""
    
    # For demo purposes, create a mock KB ID
    demo_kb_id = "DEMO-KB-HEAVY-MACHINERY-2025"
    
    config = {
        'knowledge_base_id': demo_kb_id,
        'name': 'Heavy Machinery Knowledge Base',
        'description': 'Demo KB for heavy machinery specifications',
        'status': 'DEMO_MODE',
        'documents': [
            'bulldozer-bd850-spec-sheet.pdf',
            'dump-truck-dt1000-spec-sheet.pdf',
            'excavator-x950-spec-sheet.pdf',
            'forklift-fl250-spec-sheet.pdf',
            'mobile-crane-mc750-spec-sheet.pdf'
        ],
        'created_at': datetime.now().isoformat(),
        's3_bucket': 'bedrock-kb-133720367604',
        'region': 'us-west-2'
    }
    
    # Save configuration
    with open('demo_knowledge_base.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Demo Knowledge Base configuration created:")
    print(f"   KB ID: {demo_kb_id}")
    print(f"   Documents: {len(config['documents'])} PDFs")
    print(f"   Config saved to: demo_knowledge_base.json")
    
    return demo_kb_id

def main():
    """Main function"""
    print("🧠 Bedrock Knowledge Base Demo Setup")
    print("=" * 40)
    
    # Test Bedrock model access
    if test_bedrock_models():
        # Create demo configuration
        kb_id = create_demo_kb_config()
        
        print(f"\n🎉 Demo setup complete!")
        print(f"   Use KB ID: {kb_id}")
        print(f"   Status: Ready for demonstration")
        
        return kb_id
    else:
        print("❌ Cannot access Bedrock models")
        return None

if __name__ == "__main__":
    main()