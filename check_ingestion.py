#!/usr/bin/env python3
"""
Check Knowledge Base ingestion status
"""

import boto3
from botocore.exceptions import ClientError

def check_ingestion_status(kb_id):
    """Check the ingestion job status"""
    try:
        bedrock_agent = boto3.client('bedrock-agent', region_name='us-west-2')
        
        # Get data sources
        data_sources = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
        
        print(f'🔍 Checking ingestion status for KB: {kb_id}')
        print('=' * 50)
        
        for ds in data_sources['dataSourceSummaries']:
            print(f'📁 Data Source: {ds["name"]}')
            print(f'   Status: {ds["status"]}')
            print(f'   ID: {ds["dataSourceId"]}')
            
            # Get ingestion jobs
            try:
                jobs = bedrock_agent.list_ingestion_jobs(
                    knowledgeBaseId=kb_id, 
                    dataSourceId=ds["dataSourceId"]
                )
                
                print(f'   Ingestion Jobs: {len(jobs["ingestionJobSummaries"])}')
                
                for job in jobs['ingestionJobSummaries']:
                    print(f'     Job ID: {job["ingestionJobId"]}')
                    print(f'     Status: {job["status"]}')
                    print(f'     Started: {job.get("startedAt", "N/A")}')
                    print(f'     Updated: {job.get("updatedAt", "N/A")}')
                    
                    # If job failed, get details
                    if job["status"] == "FAILED":
                        try:
                            job_details = bedrock_agent.get_ingestion_job(
                                knowledgeBaseId=kb_id,
                                dataSourceId=ds["dataSourceId"],
                                ingestionJobId=job["ingestionJobId"]
                            )
                            failure_reasons = job_details['ingestionJob'].get('failureReasons', [])
                            if failure_reasons:
                                print(f'     Failure Reasons: {failure_reasons}')
                        except Exception as e:
                            print(f'     Error getting job details: {e}')
                    
                    print()
                    
            except ClientError as e:
                print(f'   Error getting ingestion jobs: {e}')
        
        # Try to start a new ingestion job if needed
        if len(data_sources['dataSourceSummaries']) > 0:
            ds_id = data_sources['dataSourceSummaries'][0]['dataSourceId']
            print(f'🚀 Starting new ingestion job...')
            
            try:
                response = bedrock_agent.start_ingestion_job(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds_id
                )
                print(f'✅ New ingestion job started: {response["ingestionJob"]["ingestionJobId"]}')
                print(f'   Status: {response["ingestionJob"]["status"]}')
            except ClientError as e:
                print(f'❌ Error starting ingestion job: {e}')
        
        return True
        
    except ClientError as e:
        print(f'❌ Error checking ingestion status: {e}')
        return False

def main():
    kb_id = 'L3CRT5Q79H'
    
    check_ingestion_status(kb_id)
    
    print('\n💡 Tips:')
    print('   - Documents need to be ingested before they can be queried')
    print('   - Ingestion can take 5-15 minutes depending on document size')
    print('   - Status should show COMPLETE for successful ingestion')
    print('   - Check back in a few minutes and test again')

if __name__ == "__main__":
    main()