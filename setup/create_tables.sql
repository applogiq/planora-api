-- Planora API Database Setup Script
-- This script creates all the necessary tables for the Planora project management system

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS tbl_audit_logs CASCADE;
DROP TABLE IF EXISTS tbl_project_tasks CASCADE;
DROP TABLE IF EXISTS tbl_project_backlog CASCADE;
DROP TABLE IF EXISTS tbl_project_sprints CASCADE;
DROP TABLE IF EXISTS tbl_project_epics CASCADE;
DROP TABLE IF EXISTS tbl_projects CASCADE;
DROP TABLE IF EXISTS tbl_users CASCADE;
DROP TABLE IF EXISTS tbl_roles CASCADE;
DROP TABLE IF EXISTS tbl_master_project_methodology CASCADE;
DROP TABLE IF EXISTS tbl_master_project_type CASCADE;
DROP TABLE IF EXISTS tbl_master_project_status CASCADE;
DROP TABLE IF EXISTS tbl_master_priority CASCADE;

-- Master Tables

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

-- Core Tables

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

-- Projects Table
CREATE TABLE tbl_projects (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR NOT NULL,
    progress INTEGER DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    budget NUMERIC,
    spent NUMERIC DEFAULT 0.0,
    customer VARCHAR,
    customer_id VARCHAR,
    priority VARCHAR,
    team_lead_id VARCHAR REFERENCES tbl_users(id),
    team_members TEXT[],
    tags TEXT[],
    color VARCHAR,
    methodology VARCHAR,
    project_type VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Epics Table
CREATE TABLE tbl_project_epics (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    priority VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    project_id VARCHAR NOT NULL REFERENCES tbl_projects(id),
    assignee_id VARCHAR REFERENCES tbl_users(id),
    due_date TIMESTAMP WITH TIME ZONE,
    total_story_points INTEGER DEFAULT 0,
    completed_story_points INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    labels TEXT[],
    business_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Sprints Table
CREATE TABLE tbl_project_sprints (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    goal TEXT,
    total_points INTEGER DEFAULT 0,
    completed_points INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    velocity NUMERIC DEFAULT 0.0,
    project_id VARCHAR REFERENCES tbl_projects(id),
    scrum_master_id VARCHAR REFERENCES tbl_users(id),
    team_size INTEGER DEFAULT 0,
    burndown_trend VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Tasks Table
CREATE TABLE tbl_project_tasks (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR NOT NULL,
    priority VARCHAR NOT NULL,
    assignee_id VARCHAR REFERENCES tbl_users(id),
    project_id VARCHAR REFERENCES tbl_projects(id),
    sprint_id VARCHAR REFERENCES tbl_project_sprints(id),
    epic_id VARCHAR REFERENCES tbl_project_epics(id),
    sprint VARCHAR,
    labels TEXT[],
    due_date TIMESTAMP WITH TIME ZONE,
    story_points INTEGER,
    comments_count INTEGER DEFAULT 0,
    attachments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Project Backlog Table
CREATE TABLE tbl_project_backlog (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    type VARCHAR NOT NULL,
    priority VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    epic_id VARCHAR REFERENCES tbl_project_epics(id),
    epic_title VARCHAR,
    project_id VARCHAR REFERENCES tbl_projects(id),
    project_name VARCHAR,
    assignee_id VARCHAR REFERENCES tbl_users(id),
    assignee_name VARCHAR,
    reporter_id VARCHAR REFERENCES tbl_users(id),
    reporter_name VARCHAR,
    story_points INTEGER,
    business_value VARCHAR,
    effort VARCHAR,
    labels TEXT[],
    acceptance_criteria TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
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

-- Create indexes for better performance
CREATE INDEX idx_users_email ON tbl_users(email);
CREATE INDEX idx_users_role_id ON tbl_users(role_id);
CREATE INDEX idx_projects_team_lead_id ON tbl_projects(team_lead_id);
CREATE INDEX idx_projects_status ON tbl_projects(status);
CREATE INDEX idx_epics_project_id ON tbl_project_epics(project_id);
CREATE INDEX idx_epics_assignee_id ON tbl_project_epics(assignee_id);
CREATE INDEX idx_sprints_project_id ON tbl_project_sprints(project_id);
CREATE INDEX idx_tasks_assignee_id ON tbl_project_tasks(assignee_id);
CREATE INDEX idx_tasks_project_id ON tbl_project_tasks(project_id);
CREATE INDEX idx_tasks_sprint_id ON tbl_project_tasks(sprint_id);
CREATE INDEX idx_tasks_epic_id ON tbl_project_tasks(epic_id);
CREATE INDEX idx_backlog_project_id ON tbl_project_backlog(project_id);
CREATE INDEX idx_backlog_epic_id ON tbl_project_backlog(epic_id);
CREATE INDEX idx_audit_logs_user_id ON tbl_audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON tbl_audit_logs(timestamp);

-- Add comments to tables
COMMENT ON TABLE tbl_roles IS 'User roles and permissions management';
COMMENT ON TABLE tbl_users IS 'System users with profile information';
COMMENT ON TABLE tbl_projects IS 'Project management data';
COMMENT ON TABLE tbl_project_epics IS 'Project epics for organizing features';
COMMENT ON TABLE tbl_project_sprints IS 'Sprint management for agile methodology';
COMMENT ON TABLE tbl_project_tasks IS 'Individual tasks within projects';
COMMENT ON TABLE tbl_project_backlog IS 'Product backlog items';
COMMENT ON TABLE tbl_audit_logs IS 'System audit trail for tracking changes';
COMMENT ON TABLE tbl_master_priority IS 'Master data for priority levels';
COMMENT ON TABLE tbl_master_project_status IS 'Master data for project statuses';
COMMENT ON TABLE tbl_master_project_type IS 'Master data for project types';
COMMENT ON TABLE tbl_master_project_methodology IS 'Master data for project methodologies';