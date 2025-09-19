-- Migration script to convert tbl_project_tasks to tbl_project_stories
-- Run this script to migrate existing data

-- 1. Create the new stories table based on the existing tasks table
CREATE TABLE tbl_project_stories AS
SELECT
    id,
    title,
    description,
    'task' as type,  -- Set default type as 'task' for existing records
    priority,
    status,
    epic_id,
    NULL as epic_title,
    project_id,
    NULL as project_name,
    sprint_id,
    assignee_id,
    NULL as assignee_name,
    NULL as reporter_id,
    NULL as reporter_name,
    story_points,
    NULL as business_value,
    NULL as effort,
    labels,
    NULL::text[] as acceptance_criteria,
    created_at,
    updated_at
FROM tbl_project_tasks;

-- 2. Add primary key and constraints
ALTER TABLE tbl_project_stories ADD CONSTRAINT tbl_project_stories_pkey PRIMARY KEY (id);
ALTER TABLE tbl_project_stories ADD CONSTRAINT tbl_project_stories_project_id_fkey FOREIGN KEY (project_id) REFERENCES tbl_projects(id);
ALTER TABLE tbl_project_stories ADD CONSTRAINT tbl_project_stories_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES tbl_users(id);
ALTER TABLE tbl_project_stories ADD CONSTRAINT tbl_project_stories_reporter_id_fkey FOREIGN KEY (reporter_id) REFERENCES tbl_users(id);
ALTER TABLE tbl_project_stories ADD CONSTRAINT tbl_project_stories_epic_id_fkey FOREIGN KEY (epic_id) REFERENCES tbl_project_epics(id);
ALTER TABLE tbl_project_stories ADD CONSTRAINT tbl_project_stories_sprint_id_fkey FOREIGN KEY (sprint_id) REFERENCES tbl_project_sprints(id);

-- 3. Add not null constraints
ALTER TABLE tbl_project_stories ALTER COLUMN title SET NOT NULL;
ALTER TABLE tbl_project_stories ALTER COLUMN type SET NOT NULL;
ALTER TABLE tbl_project_stories ALTER COLUMN priority SET NOT NULL;
ALTER TABLE tbl_project_stories ALTER COLUMN status SET NOT NULL;

-- 4. Create indexes
CREATE INDEX ix_tbl_project_stories_id ON tbl_project_stories(id);
CREATE INDEX ix_tbl_project_stories_type ON tbl_project_stories(type);
CREATE INDEX ix_tbl_project_stories_status ON tbl_project_stories(status);
CREATE INDEX ix_tbl_project_stories_assignee_id ON tbl_project_stories(assignee_id);
CREATE INDEX ix_tbl_project_stories_project_id ON tbl_project_stories(project_id);

-- 5. Update the stories with additional information from related tables
UPDATE tbl_project_stories
SET epic_title = e.title
FROM tbl_project_epics e
WHERE tbl_project_stories.epic_id = e.id;

UPDATE tbl_project_stories
SET project_name = p.name
FROM tbl_projects p
WHERE tbl_project_stories.project_id = p.id;

UPDATE tbl_project_stories
SET assignee_name = u.name
FROM tbl_users u
WHERE tbl_project_stories.assignee_id = u.id;

-- Note: You may want to backup tbl_project_tasks before dropping it
-- RENAME TABLE tbl_project_tasks TO tbl_project_tasks_backup;