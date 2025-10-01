#!/usr/bin/env python3
"""
Temporarily Enable Public Access for Aurora PostgreSQL
This will allow direct connection from your local machine
"""

import boto3
from botocore.exceptions import ClientError

def enable_aurora_public_access():
    """Enable public access for Aurora cluster"""
    
    print("🔧 Enabling Public Access for Aurora PostgreSQL")
    print("=" * 50)
    
    try:
        rds = boto3.client('rds', region_name='us-west-2')
        
        print("⚠️  WARNING: This will temporarily make your Aurora cluster publicly accessible!")
        print("   Make sure to disable it after database setup is complete.")
        
        response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
        
        if response != 'yes':
            print("❌ Operation cancelled.")
            return False
        
        print("\n🔄 Modifying Aurora cluster to enable public access...")
        
        # Modify the cluster to enable public access
        rds.modify_db_cluster(
            DBClusterIdentifier='my-aurora-serverless',
            PubliclyAccessible=True,
            ApplyImmediately=True
        )
        
        print("✅ Aurora cluster modification initiated!")
        print("⏳ This may take 5-10 minutes to complete.")
        print("\n🔥 Once modification is complete, you can connect directly:")
        print("   python aurora_cmd_direct.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enabling public access: {e}")
        return False

def disable_aurora_public_access():
    """Disable public access for Aurora cluster"""
    
    print("🔒 Disabling Public Access for Aurora PostgreSQL")
    print("=" * 50)
    
    try:
        rds = boto3.client('rds', region_name='us-west-2')
        
        print("🔄 Modifying Aurora cluster to disable public access...")
        
        # Modify the cluster to disable public access
        rds.modify_db_cluster(
            DBClusterIdentifier='my-aurora-serverless',
            PubliclyAccessible=False,
            ApplyImmediately=True
        )
        
        print("✅ Aurora cluster public access disabled!")
        print("🔒 Your database is now secure in private subnets only.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error disabling public access: {e}")
        return False

def main():
    print("🎯 Aurora PostgreSQL Public Access Management")
    print("=" * 50)
    
    print("Choose an option:")
    print("1. Enable public access (temporary)")
    print("2. Disable public access (secure)")
    print("3. Check current status")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        enable_aurora_public_access()
    elif choice == '2':
        disable_aurora_public_access()
    elif choice == '3':
        # Check current status
        try:
            rds = boto3.client('rds', region_name='us-west-2')
            clusters = rds.describe_db_clusters(DBClusterIdentifier='my-aurora-serverless')
            cluster = clusters['DBClusters'][0]
            
            public_access = cluster.get('PubliclyAccessible', False)
            status = cluster['Status']
            
            print(f"\n📊 Current Aurora Status:")
            print(f"   Status: {status}")
            print(f"   Publicly Accessible: {public_access}")
            
            if public_access:
                print("⚠️  Cluster is currently publicly accessible")
            else:
                print("🔒 Cluster is in private subnets only")
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()