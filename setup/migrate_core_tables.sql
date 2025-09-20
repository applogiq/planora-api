-- Planora API - Core Tables Migration
-- Creates core application tables (roles, users, audit logs)

-- Drop existing core tables in reverse dependency order
DROP TABLE IF EXISTS tbl_audit_logs CASCADE;
DROP TABLE IF EXISTS tbl_users CASCADE;
DROP TABLE IF EXISTS tbl_roles CASCADE;

-- Core Tables Creation

-- Roles Table
CREATE TABLE tbl_roles (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Users Table
CREATE TABLE tbl_users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    role_id VARCHAR NOT NULL REFERENCES tbl_roles(id),
    avatar VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    department VARCHAR,
    skills TEXT[],
    phone VARCHAR,
    timezone VARCHAR
);

-- Audit Logs Table
CREATE TABLE tbl_audit_logs (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES tbl_users(id),
    user_name VARCHAR,
    action VARCHAR NOT NULL,
    resource VARCHAR NOT NULL,
    details TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR,
    user_agent TEXT,
    status VARCHAR
);

-- Indexes for better performance
CREATE INDEX idx_users_email ON tbl_users(email);
CREATE INDEX idx_users_role_id ON tbl_users(role_id);
CREATE INDEX idx_users_is_active ON tbl_users(is_active);
CREATE INDEX idx_users_department ON tbl_users(department);
CREATE INDEX idx_audit_logs_user_id ON tbl_audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON tbl_audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON tbl_audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON tbl_audit_logs(resource);

-- Comments
COMMENT ON TABLE tbl_roles IS 'User roles and permissions management';
COMMENT ON TABLE tbl_users IS 'System users with profile information';
COMMENT ON TABLE tbl_audit_logs IS 'System audit trail for tracking changes';