#!/usr/bin/env python3
"""
Aurora PostgreSQL Database Analysis and Setup Guide
Since direct connection from local machine is blocked (private subnet),
let's analyze the infrastructure and provide alternative solutions.
"""

import boto3
import json
from botocore.exceptions import ClientError

def analyze_aurora_setup():
    """Analyze the current Aurora setup and network configuration"""
    
    print("🔍 Analyzing Aurora PostgreSQL Infrastructure")
    print("=" * 55)
    
    try:
        # Check RDS clusters
        rds = boto3.client('rds', region_name='us-west-2')
        
        print("📊 Aurora Cluster Information:")
        print("-" * 30)
        
        clusters = rds.describe_db_clusters(DBClusterIdentifier='my-aurora-serverless')
        cluster = clusters['DBClusters'][0]
        
        print(f"   Cluster ID: {cluster['DBClusterIdentifier']}")
        print(f"   Status: {cluster['Status']}")
        print(f"   Engine: {cluster['Engine']} {cluster['EngineVersion']}")
        print(f"   Endpoint: {cluster['Endpoint']}")
        print(f"   Port: {cluster['Port']}")
        print(f"   VPC ID: {cluster.get('DbClusterResourceId', 'N/A')}")
        print(f"   Multi-AZ: {cluster.get('MultiAZ', False)}")
        print(f"   Publicly Accessible: {cluster.get('PubliclyAccessible', False)}")
        
        # Check subnet groups
        subnet_group = cluster.get('DBSubnetGroup', 'N/A')
        if subnet_group != 'N/A':
            print(f"   Subnet Group: {subnet_group}")
        
        # Check security groups
        vpc_security_groups = cluster.get('VpcSecurityGroups', [])
        print(f"   Security Groups: {[sg['VpcSecurityGroupId'] for sg in vpc_security_groups]}")
        
        return cluster
        
    except Exception as e:
        print(f"❌ Error analyzing Aurora setup: {e}")
        return None

def check_vpc_setup():
    """Check VPC and networking setup"""
    
    print(f"\n🌐 VPC and Networking Analysis:")
    print("-" * 35)
    
    try:
        ec2 = boto3.client('ec2', region_name='us-west-2')
        
        # Get VPC information
        vpcs = ec2.describe_vpcs()
        for vpc in vpcs['Vpcs']:
            if not vpc['IsDefault']:
                print(f"   Custom VPC: {vpc['VpcId']}")
                print(f"   CIDR: {vpc['CidrBlock']}")
                
                # Check subnets
                subnets = ec2.describe_subnets(
                    Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}]
                )
                
                print(f"   Subnets:")
                for subnet in subnets['Subnets']:
                    availability_zone = subnet['AvailabilityZone']
                    cidr = subnet['CidrBlock']
                    public = 'Public' if subnet.get('MapPublicIpOnLaunch', False) else 'Private'
                    print(f"     - {subnet['SubnetId']} ({availability_zone}) - {cidr} [{public}]")
        
    except Exception as e:
        print(f"⚠️ Could not analyze VPC setup: {e}")

def suggest_connection_methods():
    """Suggest alternative connection methods"""
    
    print(f"\n🎯 Alternative Connection Methods:")
    print("=" * 40)
    
    print("✅ Method 1: AWS CloudShell (Recommended)")
    print("-" * 40)
    print("1. Go to AWS Console → CloudShell (top right)")
    print("2. Install PostgreSQL client:")
    print("   sudo yum install -y postgresql15")
    print("3. Connect to Aurora:")
    print("   psql -h my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com \\")
    print("        -p 5432 -U dbadmin -d myapp")
    print("4. Enter password: %252m!KjPM$(5[LX")
    
    print(f"\n✅ Method 2: EC2 Instance in Same VPC")
    print("-" * 40)
    print("1. Launch an EC2 instance in the same VPC as Aurora")
    print("2. SSH to the instance")
    print("3. Install PostgreSQL client and connect")
    
    print(f"\n✅ Method 3: Enable Public Access (Temporary)")
    print("-" * 40)
    print("1. Modify Aurora cluster to enable public access")
    print("2. Update security group to allow your IP")
    print("3. Connect from local machine")
    print("4. Disable public access after setup")
    
    print(f"\n✅ Method 4: AWS Systems Manager Session Manager")
    print("-" * 40)
    print("1. Use Session Manager to access EC2 in same VPC")
    print("2. Install PostgreSQL client and connect to Aurora")

def create_cloudshell_script():
    """Create script for AWS CloudShell"""
    
    script_content = '''#!/bin/bash
# Aurora PostgreSQL Connection Script for AWS CloudShell
# Run this script in AWS CloudShell

echo "🚀 Aurora PostgreSQL Setup in AWS CloudShell"
echo "============================================="

# Install PostgreSQL client
echo "📦 Installing PostgreSQL client..."
sudo yum install -y postgresql15

# Test connection
echo "🔌 Testing connection to Aurora..."
echo "You will be prompted for password: %252m!KjPM$(5[LX"

psql -h my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com -p 5432 -U dbadmin -d myapp -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "✅ Connection successful!"
    echo ""
    echo "🔍 Running verification queries..."
    
    # Run verification queries
    psql -h my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com -p 5432 -U dbadmin -d myapp << EOF
-- Check extensions
SELECT * FROM pg_extension;

-- Check bedrock_integration schema
SELECT 
    table_schema || '.' || table_name as show_tables,
    table_type
FROM 
    information_schema.tables 
WHERE 
    table_type = 'BASE TABLE' 
AND 
    table_schema = 'bedrock_integration';

-- Check database version
SELECT version();
EOF

else
    echo "❌ Connection failed. Check the Aurora endpoint and credentials."
fi
'''
    
    with open('cloudshell_aurora_connect.sh', 'w') as f:
        f.write(script_content)
    
    print(f"\n💾 Created cloudshell_aurora_connect.sh")
    print("   Upload this script to AWS CloudShell and run it")

def provide_rds_query_editor_alternative():
    """Provide steps to use RDS Query Editor properly"""
    
    print(f"\n🔧 RDS Query Editor - Correct Connection Method:")
    print("=" * 50)
    
    print("🎯 The issue is you're using RDS Data API instead of direct connection.")
    print("Here's how to connect properly:")
    print()
    print("1. Go to RDS Console → my-aurora-serverless cluster")
    print("2. Click 'Query Editor' tab")
    print("3. For connection method, look for these options:")
    print("   ❌ Do NOT select: 'Connect using RDS Data API'")
    print("   ❌ Do NOT select: 'Connect using AWS Secrets Manager'")
    print("   ✅ DO select: 'Add new database credentials'")
    print("4. Enter manually:")
    print("   • Username: dbadmin")
    print("   • Password: %252m!KjPM$(5[LX")
    print("   • Database: myapp")
    print()
    print("🔍 If you don't see 'Add new database credentials' option:")
    print("   - Your Aurora cluster might need to be in a public subnet")
    print("   - Or you need to use AWS CloudShell/EC2 method")

def main():
    """Main analysis function"""
    
    # Analyze current setup
    cluster = analyze_aurora_setup()
    check_vpc_setup()
    
    # Provide solutions
    suggest_connection_methods()
    provide_rds_query_editor_alternative()
    create_cloudshell_script()
    
    print(f"\n" + "=" * 60)
    print("🎯 RECOMMENDED NEXT STEPS:")
    print("=" * 60)
    print("1. Try AWS CloudShell method (easiest)")
    print("2. Use the cloudshell_aurora_connect.sh script")
    print("3. If CloudShell doesn't work, try the EC2 method")
    print("4. As last resort, temporarily enable public access")
    
    print(f"\n🔥 Once connected, run the complete SQL setup script")
    print("   from the earlier message to set up vector database!")

if __name__ == "__main__":
    main()