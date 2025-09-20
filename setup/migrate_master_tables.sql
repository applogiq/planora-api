-- Planora API - Master Tables Migration
-- Creates all master data tables for lookups and configurations

-- Drop existing master tables in reverse dependency order
DROP TABLE IF EXISTS tbl_master_priority CASCADE;
DROP TABLE IF EXISTS tbl_master_project_status CASCADE;
DROP TABLE IF EXISTS tbl_master_project_type CASCADE;
DROP TABLE IF EXISTS tbl_master_project_methodology CASCADE;

-- Master Tables Creation

-- Priority Master Table
CREATE TABLE tbl_master_priority (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR,
    level INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Status Master Table
CREATE TABLE tbl_master_project_status (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Type Master Table
CREATE TABLE tbl_master_project_type (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Methodology Master Table
CREATE TABLE tbl_master_project_methodology (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for better performance
CREATE INDEX idx_master_priority_level ON tbl_master_priority(level);
CREATE INDEX idx_master_priority_sort_order ON tbl_master_priority(sort_order);
CREATE INDEX idx_master_project_status_sort_order ON tbl_master_project_status(sort_order);
CREATE INDEX idx_master_project_type_sort_order ON tbl_master_project_type(sort_order);
CREATE INDEX idx_master_project_methodology_sort_order ON tbl_master_project_methodology(sort_order);

-- Comments
COMMENT ON TABLE tbl_master_priority IS 'Master data for priority levels';
COMMENT ON TABLE tbl_master_project_status IS 'Master data for project statuses';
COMMENT ON TABLE tbl_master_project_type IS 'Master data for project types';
COMMENT ON TABLE tbl_master_project_methodology IS 'Master data for project methodologies';