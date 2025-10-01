provider "aws" {
  region = "us-west-2"  
}

# Simple data upload to S3 bucket for documents
resource "aws_s3_object" "spec_documents" {
  for_each = fileset("${path.module}/../scripts/spec-sheets/", "*.pdf")
  
  bucket = "bedrock-kb-133720367604"
  key    = "documents/${each.value}"
  source = "${path.module}/../scripts/spec-sheets/${each.value}"
  etag   = filemd5("${path.module}/../scripts/spec-sheets/${each.value}")
}

# Create a simple text file to indicate Stack 2 completion
resource "aws_s3_object" "completion_marker" {
  bucket  = "bedrock-kb-133720367604"
  key     = "stack2-completed.txt"
  content = "Stack 2 deployment completed successfully at ${timestamp()}"
}

# Output the S3 bucket information
output "s3_bucket_name" {
  value = "bedrock-kb-133720367604"
}

output "uploaded_documents" {
  value = [for file in aws_s3_object.spec_documents : file.key]
}

output "stack2_status" {
  value = "Stack 2 completed - Documents uploaded to S3"
}