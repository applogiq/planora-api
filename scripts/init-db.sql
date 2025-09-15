-- Initialize Planora Database
-- This script sets up the database with required extensions and initial data

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Create indexes for performance
-- Note: Additional indexes will be created through Alembic migrations

-- Insert default permissions
INSERT INTO permissions (id, key, description) VALUES
    (uuid_generate_v4(), 'admin.manage', 'Full administrative access'),
    (uuid_generate_v4(), 'project.create', 'Create new projects'),
    (uuid_generate_v4(), 'project.manage', 'Manage projects'),
    (uuid_generate_v4(), 'project.view', 'View projects'),
    (uuid_generate_v4(), 'task.create', 'Create new tasks'),
    (uuid_generate_v4(), 'task.update', 'Update tasks'),
    (uuid_generate_v4(), 'task.delete', 'Delete tasks'),
    (uuid_generate_v4(), 'task.view', 'View tasks'),
    (uuid_generate_v4(), 'user.manage', 'Manage users'),
    (uuid_generate_v4(), 'user.view', 'View users'),
    (uuid_generate_v4(), 'report.view', 'View reports'),
    (uuid_generate_v4(), 'report.manage', 'Manage reports'),
    (uuid_generate_v4(), 'integration.manage', 'Manage integrations'),
    (uuid_generate_v4(), 'automation.manage', 'Manage automation rules'),
    (uuid_generate_v4(), 'timetrack.manage', 'Manage time tracking')
ON CONFLICT (key) DO NOTHING;

-- Insert default integration providers
INSERT INTO integration_providers (key, display_name, description) VALUES
    ('slack', 'Slack', 'Slack workspace integration'),
    ('github', 'GitHub', 'GitHub repository integration'),
    ('gitlab', 'GitLab', 'GitLab repository integration'),
    ('gcal', 'Google Calendar', 'Google Calendar integration'),
    ('outlook', 'Outlook Calendar', 'Microsoft Outlook Calendar integration'),
    ('jira', 'Jira', 'Atlassian Jira integration'),
    ('trello', 'Trello', 'Trello board integration')
ON CONFLICT (key) DO NOTHING;

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Note: Triggers and Row-Level Security policies will be created through Alembic migrations