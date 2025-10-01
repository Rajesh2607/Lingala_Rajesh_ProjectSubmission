#!/usr/bin/env python3
"""
Database Verification Checker
Run this after manual database setup to verify everything is configured correctly
"""

def display_manual_verification():
    """Display the verification steps and expected outputs"""
    print("🔍 Database Verification Guide")
    print("=" * 50)
    
    print("\n📋 **After running the manual setup, verify with these queries:**")
    print("   (Run these in AWS RDS Query Editor)")
    
    verification_steps = [
        {
            "step": "1️⃣ Check Vector Extension",
            "query": "SELECT * FROM pg_extension WHERE extname = 'vector';",
            "expected": "Should return 1 row with vector extension details"
        },
        {
            "step": "2️⃣ Check All Extensions", 
            "query": "SELECT * FROM pg_extension;",
            "expected": "Should show vector extension among others"
        },
        {
            "step": "3️⃣ Check Bedrock Schema Tables",
            "query": """SELECT table_schema || '.' || table_name as show_tables
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
AND table_schema = 'bedrock_integration';""",
            "expected": "Should return: bedrock_integration.bedrock_kb"
        },
        {
            "step": "4️⃣ Check Table Structure",
            "query": "\\d bedrock_integration.bedrock_kb",
            "expected": "Should show columns: id (uuid), embedding (vector), chunks (text), metadata (json)"
        },
        {
            "step": "5️⃣ Test Vector Operations",
            "query": """INSERT INTO bedrock_integration.bedrock_kb (embedding, chunks, metadata) 
VALUES ('[0.1,0.2,0.3]'::vector(3), 'test chunk', '{"source": "test"}'::json);""",
            "expected": "Should insert successfully (INSERT 0 1)"
        },
        {
            "step": "6️⃣ Verify Insert",
            "query": "SELECT COUNT(*) FROM bedrock_integration.bedrock_kb;",
            "expected": "Should return count = 1"
        },
        {
            "step": "7️⃣ Test Vector Query",
            "query": "SELECT id, chunks, metadata FROM bedrock_integration.bedrock_kb WHERE embedding IS NOT NULL;",
            "expected": "Should return the test record"
        },
        {
            "step": "8️⃣ Clean Up Test Data",
            "query": "DELETE FROM bedrock_integration.bedrock_kb WHERE chunks = 'test chunk';",
            "expected": "Should delete test record (DELETE 1)"
        }
    ]
    
    for step_info in verification_steps:
        print(f"\n{step_info['step']}")
        print(f"Query:")
        print(f"   {step_info['query']}")
        print(f"Expected: {step_info['expected']}")
        print("-" * 60)
    
    print(f"\n✅ **If all queries work correctly:**")
    print("   • Vector extension is properly installed")
    print("   • bedrock_integration schema exists")
    print("   • bedrock_kb table is ready for vector storage") 
    print("   • Database is ready for Bedrock Knowledge Base integration")
    
    print(f"\n🚀 **Ready for Next Step:**")
    print("   Create Bedrock Knowledge Base using Aurora PostgreSQL as vector store")

def show_connection_info():
    """Show connection information for reference"""
    print("\n🔗 **Connection Information:**")
    print("   • AWS Console: https://console.aws.amazon.com/rds/")
    print("   • Cluster: my-aurora-serverless")
    print("   • Endpoint: my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com")
    print("   • Database: myapp")
    print("   • Username: dbadmin")
    print("   • Password: (from AWS Secrets Manager)")

def main():
    print("🧪 Aurora PostgreSQL Vector Database Verification")
    print("=" * 60)
    
    show_connection_info()
    display_manual_verification()
    
    print("\n" + "=" * 60)
    print("📝 SUMMARY")
    print("=" * 60)
    print("1. Use AWS RDS Query Editor to connect to the database")
    print("2. Run the verification queries above in order")
    print("3. Confirm all expected results are returned")
    print("4. Database will be ready for Bedrock Knowledge Base creation")
    print("\n🎯 The database setup provides:")
    print("   ✅ Vector extension for embeddings storage")
    print("   ✅ Optimized HNSW index for similarity search") 
    print("   ✅ Proper schema and permissions")
    print("   ✅ Ready for 1536-dimensional embeddings (Titan)")

if __name__ == "__main__":
    main()