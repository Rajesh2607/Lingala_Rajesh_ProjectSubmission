#!/usr/bin/env python3
"""
Script to create the required index in OpenSearch Serverless for Bedrock Knowledge Base
"""
import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
import time

def create_opensearch_index():
    # AWS configuration
    region = 'us-west-2'
    service = 'aoss'
    collection_endpoint = 'https://j0ids6fbmpf6dmltgom1.us-west-2.aoss.amazonaws.com'
    index_name = 'bedrock-index'
    
    # Create AWS credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    # Index mapping for Bedrock Knowledge Base
    index_mapping = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 512,
                "knn.algo_param.ef_construction": 512,
                "knn.space_type": "cosinesimil"
            }
        },
        "mappings": {
            "properties": {
                "bedrock-vector": {
                    "type": "knn_vector",
                    "dimension": 1536,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": 512,
                            "ef_search": 512,
                            "m": 16
                        }
                    }
                },
                "bedrock-text": {
                    "type": "text"
                },
                "bedrock-metadata": {
                    "type": "text"
                }
            }
        }
    }
    
    # Create the index
    url = f"{collection_endpoint}/{index_name}"
    print(f"Creating index at: {url}")
    
    try:
        response = requests.put(
            url,
            auth=awsauth,
            json=index_mapping,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Index created successfully!")
            return True
        else:
            print(f"❌ Failed to create index: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        return False

if __name__ == "__main__":
    print("Creating OpenSearch Serverless index for Bedrock Knowledge Base...")
    success = create_opensearch_index()
    if success:
        print("🎉 Index creation completed successfully!")
    else:
        print("💥 Index creation failed!")