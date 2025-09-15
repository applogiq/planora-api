-- Setup script for Planora PostgreSQL database
-- Run this as PostgreSQL superuser (usually 'postgres')

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'planora') THEN
        CREATE USER planora WITH PASSWORD 'password';
    END IF;
END
$$;

-- Create database (if not exists)
SELECT 'CREATE DATABASE planora OWNER planora'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'planora')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE planora TO planora;

-- Connect to the planora database
\c planora

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO planora;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO planora;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO planora;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Display confirmation
SELECT 'Planora database setup completed successfully!' as message;