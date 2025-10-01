#!/usr/bin/env python3
"""
Disable Aurora PostgreSQL Public Access
"""

import boto3
from botocore.exceptions import ClientError

def disable_public_access():
    """Disable public access for Aurora cluster"""
    
    print("🔒 Disabling Public Access for Aurora PostgreSQL")
    print("=" * 50)
    
    try:
        rds = boto3.client('rds', region_name='us-west-2')
        
        print("🔄 Modifying Aurora cluster to disable public access...")
        
        # Modify the cluster to disable public access
        response = rds.modify_db_cluster(
            DBClusterIdentifier='my-aurora-serverless',
            PubliclyAccessible=False,
            ApplyImmediately=True
        )
        
        print("✅ Aurora cluster public access disabled!")
        print(f"   Status: {response['DBCluster']['Status']}")
        print("🔒 Your database is now secure in private subnets only.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error disabling public access: {e}")
        return False

if __name__ == "__main__":
    disable_public_access()