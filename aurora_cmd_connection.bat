@echo off
REM ============================================================================
REM Aurora PostgreSQL Connection via Command Line (Windows)
REM ============================================================================

echo 🚀 Aurora PostgreSQL Command Line Connection Setup
echo ====================================================

echo.
echo 📋 Database Connection Details:
echo ================================
echo Host: my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com
echo Port: 5432
echo Database: myapp  
echo Username: dbadmin
echo Password: %%252m!KjPM$(5[LX

echo.
echo 🔧 Step 1: Install PostgreSQL Client Tools
echo ===========================================
echo Option A - Using winget (Windows Package Manager):
echo   winget install PostgreSQL.PostgreSQL
echo.
echo Option B - Using Chocolatey (if installed):
echo   choco install postgresql
echo.
echo Option C - Manual Download:
echo   Visit: https://www.postgresql.org/download/windows/
echo   Download PostgreSQL installer
echo   During installation, make sure to include "Command Line Tools"

echo.
echo 🔌 Step 2: Connect to Aurora PostgreSQL
echo ========================================
echo After installation, run this command:
echo.
echo psql -h my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com -p 5432 -U dbadmin -d myapp
echo.
echo When prompted for password, enter: %%252m!KjPM$(5[LX
echo (Note: Password will not be visible while typing)

echo.
echo ✅ Step 3: Once Connected, Run These Queries
echo =============================================
echo 1. Check database version:
echo    SELECT version();
echo.
echo 2. Check extensions:
echo    SELECT * FROM pg_extension;
echo.
echo 3. Check bedrock_integration schema:
echo    SELECT table_schema ^|^| '.' ^|^| table_name as show_tables
echo    FROM information_schema.tables 
echo    WHERE table_type = 'BASE TABLE' 
echo    AND table_schema = 'bedrock_integration';

echo.
echo 🛠️ Step 4: If Database Setup Needed
echo ====================================
echo Run the complete SQL setup script from vector_database_setup.sql

echo.
echo 🎯 Alternative: Use Docker PostgreSQL Client
echo =============================================
echo If you have Docker installed:
echo docker run -it --rm postgres:15 psql -h my-aurora-serverless.cluster-cu2bffdza994.us-west-2.rds.amazonaws.com -p 5432 -U dbadmin -d myapp

pause