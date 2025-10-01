#!/usr/bin/env python3
"""
Enable Aurora PostgreSQL Public Access
"""

import boto3
from botocore.exceptions import ClientError

def enable_public_access():
    """Enable public access for Aurora cluster"""
    
    print("🔧 Enabling Public Access for Aurora PostgreSQL")
    print("=" * 50)
    
    try:
        rds = boto3.client('rds', region_name='us-west-2')
        
        print("🔄 Modifying Aurora cluster to enable public access...")
        print("⚠️  This will temporarily make your Aurora cluster publicly accessible!")
        
        # Modify the cluster to enable public access
        response = rds.modify_db_cluster(
            DBClusterIdentifier='my-aurora-serverless',
            PubliclyAccessible=True,
            ApplyImmediately=True
        )
        
        print("✅ Aurora cluster modification initiated!")
        print(f"   Status: {response['DBCluster']['Status']}")
        print("⏳ Modification will take 5-10 minutes to complete.")
        
        print("\n🔥 Once modification is complete, you can connect directly using:")
        print("   python aurora_cmd_direct.py")
        
        print("\n🔒 IMPORTANT: After database setup, disable public access with:")
        print("   python aurora_disable_public.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enabling public access: {e}")
        return False

if __name__ == "__main__":
    enable_public_access()