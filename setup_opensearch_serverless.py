#!/usr/bin/env python3
"""
Create OpenSearch Serverless Security Policies and Collection
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

class OpenSearchServerlessSetup:
    def __init__(self):
        self.region = 'us-west-2'
        self.opensearch_serverless = boto3.client('opensearchserverless', region_name=self.region)
        self.collection_name = "heavy-machinery-kb"  # Shortened name
        self.policy_name = "machinery-kb"  # Shortened for 32 char limit
        
    def create_encryption_policy(self):
        """Create encryption policy for the collection"""
        print("🔧 Creating encryption policy...")
        
        policy_document = {
            "Rules": [
                {
                    "ResourceType": "collection",
                    "Resource": [f"collection/{self.collection_name}"]
                }
            ],
            "AWSOwnedKey": True
        }
        
        try:
            response = self.opensearch_serverless.create_security_policy(
                name=f"{self.policy_name}-encryption",
                type='encryption',
                policy=json.dumps(policy_document),
                description='Encryption policy for heavy machinery knowledge base collection'
            )
            print(f"✅ Created encryption policy: {response['securityPolicyDetail']['name']}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                print(f"ℹ️ Encryption policy already exists")
                return True
            else:
                print(f"❌ Error creating encryption policy: {e}")
                return False
    
    def create_network_policy(self):
        """Create network policy for the collection"""
        print("🔧 Creating network policy...")
        
        policy_document = [
            {
                "Rules": [
                    {
                        "ResourceType": "collection",
                        "Resource": [f"collection/{self.collection_name}"]
                    },
                    {
                        "ResourceType": "dashboard",
                        "Resource": [f"collection/{self.collection_name}"]
                    }
                ],
                "AllowFromPublic": True
            }
        ]
        
        try:
            response = self.opensearch_serverless.create_security_policy(
                name=f"{self.policy_name}-network",
                type='network',
                policy=json.dumps(policy_document),
                description='Network policy for heavy machinery knowledge base collection'
            )
            print(f"✅ Created network policy: {response['securityPolicyDetail']['name']}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                print(f"ℹ️ Network policy already exists")
                return True
            else:
                print(f"❌ Error creating network policy: {e}")
                return False
    
    def get_current_user_arn(self):
        """Get current user ARN for data access policy"""
        try:
            sts = boto3.client('sts', region_name=self.region)
            identity = sts.get_caller_identity()
            return identity['Arn']
        except Exception as e:
            print(f"❌ Error getting user ARN: {e}")
            return None
    
    def create_data_access_policy(self):
        """Create data access policy for the collection"""
        print("🔧 Creating data access policy...")
        
        user_arn = self.get_current_user_arn()
        if not user_arn:
            print("❌ Cannot create data access policy without user ARN")
            return False
        
        print(f"   Using principal: {user_arn}")
        
        policy_document = [
            {
                "Rules": [
                    {
                        "ResourceType": "collection",
                        "Resource": [f"collection/{self.collection_name}"],
                        "Permission": [
                            "aoss:CreateCollectionItems",
                            "aoss:DeleteCollectionItems", 
                            "aoss:UpdateCollectionItems",
                            "aoss:DescribeCollectionItems"
                        ]
                    },
                    {
                        "ResourceType": "index",
                        "Resource": [f"index/{self.collection_name}/*"],
                        "Permission": [
                            "aoss:CreateIndex",
                            "aoss:DeleteIndex",
                            "aoss:UpdateIndex", 
                            "aoss:DescribeIndex",
                            "aoss:ReadDocument",
                            "aoss:WriteDocument"
                        ]
                    }
                ],
                "Principal": [user_arn]
            }
        ]
        
        try:
            response = self.opensearch_serverless.create_access_policy(
                name=f"{self.policy_name}-access",
                type='data',
                policy=json.dumps(policy_document),
                description='Data access policy for heavy machinery knowledge base collection'
            )
            print(f"✅ Created data access policy: {response['accessPolicyDetail']['name']}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                print(f"ℹ️ Data access policy already exists")
                return True
            else:
                print(f"❌ Error creating data access policy: {e}")
                return False
    
    def create_collection(self):
        """Create the OpenSearch Serverless collection"""
        print("🔧 Creating OpenSearch Serverless collection...")
        
        try:
            collection_response = self.opensearch_serverless.create_collection(
                name=self.collection_name,
                type='VECTORSEARCH',
                description='Vector collection for heavy machinery knowledge base'
            )
            
            collection_id = collection_response['createCollectionDetail']['id']
            collection_arn = collection_response['createCollectionDetail']['arn']
            
            print(f"✅ Created OpenSearch collection: {collection_id}")
            print(f"   ARN: {collection_arn}")
            
            # Wait for collection to be active
            print("⏳ Waiting for collection to be active...")
            max_attempts = 20
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    collection_status = self.opensearch_serverless.batch_get_collection(
                        ids=[collection_id]
                    )
                    
                    if collection_status['collectionDetails']:
                        status = collection_status['collectionDetails'][0]['status']
                        print(f"   Collection status: {status}")
                        
                        if status == 'ACTIVE':
                            endpoint = collection_status['collectionDetails'][0]['collectionEndpoint']
                            print(f"✅ Collection is active with endpoint: {endpoint}")
                            return {
                                'collection_id': collection_id,
                                'collection_arn': collection_arn,
                                'endpoint': endpoint
                            }
                        elif status == 'FAILED':
                            raise Exception("Collection creation failed")
                    
                    attempt += 1
                    time.sleep(30)
                    
                except Exception as e:
                    print(f"   Error checking status: {e}")
                    attempt += 1
                    time.sleep(30)
            
            raise Exception("Collection did not become active within expected time")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                print(f"ℹ️ Collection {self.collection_name} already exists")
                # Get existing collection
                try:
                    collections = self.opensearch_serverless.list_collections()
                    for collection in collections['collectionSummaries']:
                        if collection['name'] == self.collection_name:
                            return {
                                'collection_id': collection['id'],
                                'collection_arn': collection['arn'],
                                'endpoint': collection.get('endpoint', '')
                            }
                except Exception as list_error:
                    print(f"Error listing collections: {list_error}")
                    return None
            else:
                print(f"❌ Error creating OpenSearch collection: {e}")
                return None
    
    def setup_complete_opensearch(self):
        """Set up complete OpenSearch Serverless with all required policies"""
        print("🚀 Setting up OpenSearch Serverless for Bedrock Knowledge Base")
        print("=" * 70)
        
        # Step 1: Create encryption policy
        if not self.create_encryption_policy():
            return None
        
        # Step 2: Create network policy  
        if not self.create_network_policy():
            return None
        
        # Step 3: Create data access policy
        if not self.create_data_access_policy():
            return None
        
        # Wait a bit for policies to propagate
        print("⏳ Waiting for policies to propagate...")
        time.sleep(10)
        
        # Step 4: Create collection
        collection_info = self.create_collection()
        
        if collection_info:
            print("\n" + "=" * 70)
            print("🎉 OpenSearch Serverless Setup Complete!")
            print("=" * 70)
            print(f"Collection Name: {self.collection_name}")
            print(f"Collection ID: {collection_info['collection_id']}")
            print(f"Collection ARN: {collection_info['collection_arn']}")
            print(f"Endpoint: {collection_info.get('endpoint', 'Pending...')}")
            
            return collection_info
        else:
            print("❌ OpenSearch setup failed")
            return None

def main():
    setup = OpenSearchServerlessSetup()
    collection_info = setup.setup_complete_opensearch()
    
    if collection_info:
        print(f"\n✅ Ready to create Bedrock Knowledge Base!")
        print(f"Use collection ARN: {collection_info['collection_arn']}")
    else:
        print(f"\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()