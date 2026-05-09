-- MAMA-LENS AI — Database Initialization Script
-- PostgreSQL 15+

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- For accent-insensitive search

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'patient', 'community_health_worker', 'midwife', 'doctor',
        'specialist', 'ngo_staff', 'clinic_admin', 'system_admin'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE user_status AS ENUM (
        'active', 'inactive', 'suspended', 'pending_verification'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM ('low', 'moderate', 'high', 'emergency');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Performance indexes (created after SQLAlchemy creates tables)
-- These will be created by Alembic migrations

-- Seed initial data: Emergency contacts
-- (Actual seeding done via Python seed scripts)

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mamalens;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mamalens;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO mamalens;

-- Row-level security (for multi-tenant support)
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;

COMMENT ON DATABASE mamalens_db IS 'MAMA-LENS AI — Maternal Assessment & Monitoring for Early Loss Support';
