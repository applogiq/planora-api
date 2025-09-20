-- Planora API - Project Tables Migration
-- Creates project management tables (projects, epics, sprints, tasks, backlog)

-- Drop existing project tables in reverse dependency order
DROP TABLE IF EXISTS tbl_project_tasks CASCADE;
DROP TABLE IF EXISTS tbl_project_backlog CASCADE;
DROP TABLE IF EXISTS tbl_project_sprints CASCADE;
DROP TABLE IF EXISTS tbl_project_epics CASCADE;
DROP TABLE IF EXISTS tbl_projects CASCADE;

-- Project Management Tables Creation

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

-- Indexes for better performance
CREATE INDEX idx_projects_team_lead_id ON tbl_projects(team_lead_id);
CREATE INDEX idx_projects_status ON tbl_projects(status);
CREATE INDEX idx_projects_priority ON tbl_projects(priority);
CREATE INDEX idx_epics_project_id ON tbl_project_epics(project_id);
CREATE INDEX idx_epics_assignee_id ON tbl_project_epics(assignee_id);
CREATE INDEX idx_epics_status ON tbl_project_epics(status);
CREATE INDEX idx_sprints_project_id ON tbl_project_sprints(project_id);
CREATE INDEX idx_sprints_status ON tbl_project_sprints(status);
CREATE INDEX idx_tasks_assignee_id ON tbl_project_tasks(assignee_id);
CREATE INDEX idx_tasks_project_id ON tbl_project_tasks(project_id);
CREATE INDEX idx_tasks_sprint_id ON tbl_project_tasks(sprint_id);
CREATE INDEX idx_tasks_epic_id ON tbl_project_tasks(epic_id);
CREATE INDEX idx_tasks_status ON tbl_project_tasks(status);
CREATE INDEX idx_backlog_project_id ON tbl_project_backlog(project_id);
CREATE INDEX idx_backlog_epic_id ON tbl_project_backlog(epic_id);
CREATE INDEX idx_backlog_assignee_id ON tbl_project_backlog(assignee_id);
CREATE INDEX idx_backlog_status ON tbl_project_backlog(status);

-- Comments
COMMENT ON TABLE tbl_projects IS 'Project management data';
COMMENT ON TABLE tbl_project_epics IS 'Project epics for organizing features';
COMMENT ON TABLE tbl_project_sprints IS 'Sprint management for agile methodology';
COMMENT ON TABLE tbl_project_tasks IS 'Individual tasks within projects';
COMMENT ON TABLE tbl_project_backlog IS 'Product backlog items';