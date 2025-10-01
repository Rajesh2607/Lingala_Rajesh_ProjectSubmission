-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create bedrock_integration schema
CREATE SCHEMA IF NOT EXISTS bedrock_integration;

-- Create bedrock_user role
DO $$ BEGIN
    CREATE ROLE bedrock_user LOGIN;
EXCEPTION WHEN duplicate_object THEN
    RAISE NOTICE 'Role bedrock_user already exists';
END $$;

-- Grant permissions on schema
GRANT ALL ON SCHEMA bedrock_integration TO bedrock_user;

-- Set password for bedrock_user (replace 'your_password' with actual password)
ALTER ROLE bedrock_user PASSWORD 'BedrockUser2024!';

-- Switch to bedrock_user (optional - can be done in separate session)
-- SET SESSION AUTHORIZATION bedrock_user;

-- Create the main table for vector storage
CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding vector(1536),
    chunks text,
    metadata json
);

-- Create vector index for similarity search
CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx 
ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);

-- Grant permissions on table to bedrock_user
GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;

-- Create additional indexes for better performance
CREATE INDEX IF NOT EXISTS bedrock_kb_metadata_idx 
ON bedrock_integration.bedrock_kb USING gin (metadata);

-- Check extensions
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check schema and tables
SELECT table_schema || '.' || table_name as show_tables
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
AND table_schema = 'bedrock_integration';

-- Check table structure
\d bedrock_integration.bedrock_kb

-- Test vector operations (optional)
-- INSERT INTO bedrock_integration.bedrock_kb (embedding, chunks, metadata) 
-- VALUES ('[0.1,0.2,0.3]'::vector, 'test chunk', '{"source": "test"}'::json);

-- Check if data was inserted
-- SELECT COUNT(*) FROM bedrock_integration.bedrock_kb;