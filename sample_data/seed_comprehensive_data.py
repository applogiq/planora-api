#!/usr/bin/env python3
"""
Comprehensive sample data seeding for Planora API
Creates sample projects, tasks, resources, integrations, automation, and reports
"""

import sys
from pathlib import Path
import uuid
from datetime import datetime, date, timedelta
import json

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import (
    # Core entities
    Tenant, User, UserProfile, Role, UserRole,
    # Projects & Tasks
    Project, ProjectMember, Task, Board, BoardColumn, Sprint, Comment, Label, TaskLabel,
    CustomField, TaskCustomField, Attachment, TaskHistory, TaskWatcher,
    # Resources & Time
    TimeEntry, Timesheet, BillingRate, Allocation, CapacityCalendar,
    # Integrations
    IntegrationProvider, OAuthToken, IntegrationSubscription, WebhookEndpoint, ExternalLink,
    # Automation
    AutomationRule, AutomationVersion, AutomationRun, Webhook, WebhookDelivery,
    # Reporting
    Report, ReportJob, ReportSchedule, MetricsStore, AnalyticsEvent, Dashboard, DashboardWidget, SavedFilter
)

def get_sample_data_context(session):
    """Get existing users and tenant for sample data creation"""
    tenant = session.query(Tenant).first()
    if not tenant:
        print("No tenant found! Please run seed_sample_users.py first.")
        return None
    
    users = session.query(User).all()
    if not users:
        print("No users found! Please run seed_sample_users.py first.")
        return None
    
    # Create user lookup by email for easy reference
    user_map = {user.email: user for user in users}
    
    # Use existing user as default for all roles if specific users don't exist
    default_user = users[0]
    
    return {
        'tenant': tenant,
        'users': users,
        'user_map': user_map,
        'admin_user': user_map.get('admin@planora.com', default_user),
        'pm_user': user_map.get('pm@planora.com', default_user),
        'dev_user': user_map.get('developer@planora.com', default_user),
        'designer_user': user_map.get('designer@planora.com', default_user),
        'tester_user': user_map.get('tester@planora.com', default_user)
    }

def create_sample_projects(session, context):
    """Create sample projects with different types and statuses"""
    tenant = context['tenant']
    admin_user = context['admin_user']
    pm_user = context['pm_user']
    
    projects_data = [
        {
            'key': 'WEB',
            'name': 'Website Redesign',
            'description': 'Complete redesign of company website with modern UI/UX',
            'status': 'active',
            'start_date': date.today() - timedelta(days=30),
            'due_date': date.today() + timedelta(days=60),
            'owner': admin_user
        },
        {
            'key': 'MOB',
            'name': 'Mobile App Development',
            'description': 'Native mobile application for iOS and Android',
            'status': 'active',
            'start_date': date.today() - timedelta(days=45),
            'due_date': date.today() + timedelta(days=90),
            'owner': pm_user
        },
        {
            'key': 'API',
            'name': 'API v2.0 Migration',
            'description': 'Migration to new API architecture with improved performance',
            'status': 'active',
            'start_date': date.today() - timedelta(days=60),
            'due_date': date.today() + timedelta(days=30),
            'owner': admin_user
        },
        {
            'key': 'MKT',
            'name': 'Marketing Campaign Q4',
            'description': 'Q4 marketing campaign for product launch',
            'status': 'planning',
            'start_date': date.today() + timedelta(days=15),
            'due_date': date.today() + timedelta(days=120),
            'owner': pm_user
        },
        {
            'key': 'ARCH',
            'name': 'Architecture Review',
            'description': 'Comprehensive architecture review and documentation',
            'status': 'completed',
            'start_date': date.today() - timedelta(days=90),
            'due_date': date.today() - timedelta(days=30),
            'owner': admin_user
        }
    ]
    
    projects = []
    for proj_data in projects_data:
        project = Project(
            tenant_id=tenant.id,
            key=proj_data['key'],
            name=proj_data['name'],
            description=proj_data['description'],
            status=proj_data['status'],
            start_date=proj_data['start_date'],
            due_date=proj_data['due_date'],
            owner_user_id=proj_data['owner'].id
        )
        session.add(project)
        projects.append(project)
    
    session.flush()
    
    # Add project members
    for i, project in enumerate(projects):
        # Add owner as project owner
        owner_member = ProjectMember(
            project_id=project.id,
            user_id=project.owner_user_id,
            role='Owner'
        )
        session.add(owner_member)
        
        # Add other team members
        team_members = [
            (context['dev_user'], 'Member'),
            (context['designer_user'], 'Member'),
            (context['tester_user'], 'Member')
        ]
        
        if project.owner_user_id != pm_user.id:
            team_members.append((pm_user, 'PM'))
        
        for user, role in team_members:
            if user and user.id != project.owner_user_id:
                member = ProjectMember(
                    project_id=project.id,
                    user_id=user.id,
                    role=role
                )
                session.add(member)
    
    session.commit()
    print(f"Created {len(projects)} sample projects")
    return projects

def create_sample_boards_and_sprints(session, context, projects):
    """Create sample boards and sprints for projects"""
    tenant = context['tenant']
    
    boards = []
    sprints = []
    
    for project in projects[:3]:  # Only for active projects
        # Create board
        board = Board(
            tenant_id=tenant.id,
            project_id=project.id,
            name=f"{project.name} Board"
        )
        session.add(board)
        session.flush()
        
        # Create board columns
        columns_data = [
            ('To Do', 0, 5),
            ('In Progress', 1, 3),
            ('Review', 2, 2),
            ('Done', 3, None)
        ]
        
        for col_name, position, wip_limit in columns_data:
            column = BoardColumn(
                board_id=board.id,
                name=col_name,
                position=position,
                wip_limit=wip_limit
            )
            session.add(column)
        
        boards.append(board)
        
        # Create sprints
        if project.status == 'active':
            sprint_data = [
                ('Sprint 1', date.today() - timedelta(days=14), date.today(), 'completed'),
                ('Sprint 2', date.today(), date.today() + timedelta(days=14), 'active'),
                ('Sprint 3', date.today() + timedelta(days=14), date.today() + timedelta(days=28), 'planned')
            ]
            
            for sprint_name, start_date, end_date, state in sprint_data:
                sprint = Sprint(
                    tenant_id=tenant.id,
                    project_id=project.id,
                    name=sprint_name,
                    start_date=start_date,
                    end_date=end_date,
                    state=state,
                    goal=f"Complete key features for {project.name}"
                )
                session.add(sprint)
                sprints.append(sprint)
    
    session.commit()
    print(f"Created {len(boards)} boards and {len(sprints)} sprints")
    return boards, sprints

def create_sample_tasks(session, context, projects, sprints):
    """Create sample tasks with various statuses and assignments"""
    tenant = context['tenant']
    users = context['users']
    
    # Create labels first
    labels_data = [
        ('Bug', '#ff0000'),
        ('Feature', '#00ff00'),
        ('Enhancement', '#0000ff'),
        ('Urgent', '#ff6600'),
        ('Documentation', '#800080')
    ]
    
    labels = []
    for label_name, color in labels_data:
        label = Label(
            tenant_id=tenant.id,
            name=label_name,
            color_hex=color
        )
        session.add(label)
        labels.append(label)
    
    session.flush()
    
    # Create custom fields
    custom_fields_data = [
        ('Story Points', 'number', '{"min": 1, "max": 20}'),
        ('Business Value', 'select', '{"options": ["High", "Medium", "Low"]}'),
        ('Epic Link', 'text', '{}')
    ]
    
    custom_fields = []
    for field_name, field_type, config in custom_fields_data:
        field = CustomField(
            tenant_id=tenant.id,
            name=field_name,
            type=field_type,
            config_json=config
        )
        session.add(field)
        custom_fields.append(field)
    
    session.flush()
    
    # Create tasks
    tasks = []
    task_counter = 1
    
    for project in projects:
        project_sprints = [s for s in sprints if s.project_id == project.id]
        current_sprint = next((s for s in project_sprints if s.state == 'active'), None)
        
        # Epic tasks
        epic_tasks_data = [
            {
                'title': f'{project.name} Architecture Design',
                'type': 'epic',
                'status': 'Done' if project.status == 'completed' else 'In Progress',
                'priority': 'high',
                'assignee': context['admin_user'],
                'reporter': context['admin_user'],
                'story_points': 13,
                'description': 'Design the overall architecture and technical specifications'
            },
            {
                'title': f'{project.name} User Interface',
                'type': 'epic', 
                'status': 'In Progress',
                'priority': 'high',
                'assignee': context['designer_user'],
                'reporter': context['pm_user'],
                'story_points': 21,
                'description': 'Design and implement user interface components'
            }
        ]
        
        for epic_data in epic_tasks_data:
            task = Task(
                tenant_id=tenant.id,
                project_id=project.id,
                sprint_id=current_sprint.id if current_sprint else None,
                key=f"{project.key}-{task_counter}",
                title=epic_data['title'],
                description_md=epic_data['description'],
                type=epic_data['type'],
                status=epic_data['status'],
                priority=epic_data['priority'],
                assignee_id=epic_data['assignee'].id if epic_data['assignee'] else None,
                reporter_id=epic_data['reporter'].id if epic_data['reporter'] else None,
                story_points=epic_data['story_points'],
                due_date=date.today() + timedelta(days=30) if epic_data['status'] != 'Done' else None
            )
            session.add(task)
            tasks.append(task)
            task_counter += 1
        
        session.flush()
        
        # Regular tasks
        regular_tasks_data = [
            {
                'title': 'Set up development environment',
                'type': 'task',
                'status': 'Done',
                'priority': 'medium',
                'assignee': context['dev_user'],
                'reporter': context['pm_user'],
                'story_points': 3,
                'parent': tasks[-2]  # Link to first epic
            },
            {
                'title': 'Create database schema',
                'type': 'task',
                'status': 'Done',
                'priority': 'high',
                'assignee': context['dev_user'],
                'reporter': context['admin_user'],
                'story_points': 5,
                'parent': tasks[-2]
            },
            {
                'title': 'Design user authentication flow',
                'type': 'task',
                'status': 'In Progress',
                'priority': 'high',
                'assignee': context['designer_user'],
                'reporter': context['pm_user'],
                'story_points': 8,
                'parent': tasks[-1]  # Link to second epic
            },
            {
                'title': 'Implement user registration',
                'type': 'task',
                'status': 'To Do',
                'priority': 'medium',
                'assignee': context['dev_user'],
                'reporter': context['pm_user'],
                'story_points': 5,
                'parent': tasks[-1]
            },
            {
                'title': 'Write unit tests for API endpoints',
                'type': 'task',
                'status': 'To Do',
                'priority': 'medium',
                'assignee': context['tester_user'],
                'reporter': context['dev_user'],
                'story_points': 8,
                'parent': tasks[-2]
            }
        ]
        
        # Bug tasks
        bug_tasks_data = [
            {
                'title': 'Login form validation not working',
                'type': 'bug',
                'status': 'In Progress',
                'priority': 'high',
                'assignee': context['dev_user'],
                'reporter': context['tester_user'],
                'story_points': 3
            },
            {
                'title': 'Performance issue with large datasets',
                'type': 'bug',
                'status': 'To Do',
                'priority': 'medium',
                'assignee': context['dev_user'],
                'reporter': context['admin_user'],
                'story_points': 5
            }
        ]
        
        all_task_data = regular_tasks_data + bug_tasks_data
        
        for task_data in all_task_data:
            task = Task(
                tenant_id=tenant.id,
                project_id=project.id,
                parent_task_id=task_data.get('parent').id if task_data.get('parent') else None,
                sprint_id=current_sprint.id if current_sprint and task_data['status'] != 'To Do' else None,
                key=f"{project.key}-{task_counter}",
                title=task_data['title'],
                description_md=f"## Description\n\n{task_data['title']}\n\n## Acceptance Criteria\n\n- [ ] Implementation complete\n- [ ] Tests written\n- [ ] Code reviewed",
                type=task_data['type'],
                status=task_data['status'],
                priority=task_data['priority'],
                assignee_id=task_data['assignee'].id if task_data['assignee'] else None,
                reporter_id=task_data['reporter'].id if task_data['reporter'] else None,
                story_points=task_data['story_points'],
                due_date=date.today() + timedelta(days=14) if task_data['status'] in ['To Do', 'In Progress'] else None
            )
            session.add(task)
            tasks.append(task)
            task_counter += 1
    
    session.commit()
    
    # Add labels to tasks
    for i, task in enumerate(tasks):
        if task.type == 'bug':
            task_label = TaskLabel(task_id=task.id, label_id=labels[0].id)  # Bug label
            session.add(task_label)
        elif task.type == 'epic':
            task_label = TaskLabel(task_id=task.id, label_id=labels[1].id)  # Feature label
            session.add(task_label)
        
        if task.priority == 'high':
            task_label = TaskLabel(task_id=task.id, label_id=labels[3].id)  # Urgent label
            session.add(task_label)
    
    # Add custom field values
    for task in tasks:
        if task.story_points:
            custom_field_value = TaskCustomField(
                task_id=task.id,
                field_id=custom_fields[0].id,  # Story Points
                value_json=str(int(task.story_points))
            )
            session.add(custom_field_value)
        
        # Business Value
        business_value = 'High' if task.priority == 'high' else 'Medium' if task.priority == 'medium' else 'Low'
        custom_field_value = TaskCustomField(
            task_id=task.id,
            field_id=custom_fields[1].id,  # Business Value
            value_json=f'"{business_value}"'
        )
        session.add(custom_field_value)
    
    session.commit()
    
    # Add comments to some tasks
    for task in tasks[:10]:  # Add comments to first 10 tasks
        comment = Comment(
            tenant_id=tenant.id,
            task_id=task.id,
            author_user_id=context['pm_user'].id,
            body_md=f"This task is progressing well. Current status: {task.status}"
        )
        session.add(comment)
        
        # Add a follow-up comment
        if task.assignee_id:
            follow_up = Comment(
                tenant_id=tenant.id,
                task_id=task.id,
                author_user_id=task.assignee_id,
                body_md="Thanks for the update! I'll keep working on this."
            )
            session.add(follow_up)
    
    session.commit()
    print(f"Created {len(tasks)} sample tasks with labels, custom fields, and comments")
    return tasks

def create_sample_time_tracking(session, context, tasks):
    """Create sample time entries and resource data"""
    tenant = context['tenant']
    users = context['users']
    
    # Create billing rates
    billing_rates = []
    for user in users:
        if user.email in ['admin@planora.com', 'pm@planora.com']:
            rate = 150.00
        elif user.email in ['developer@planora.com', 'designer@planora.com']:
            rate = 120.00
        elif user.email == 'tester@planora.com':
            rate = 100.00
        else:
            rate = 75.00
        
        billing_rate = BillingRate(
            tenant_id=tenant.id,
            user_id=user.id,
            hourly_rate=rate,
            currency='USD',
            effective_from=date.today() - timedelta(days=90)
        )
        session.add(billing_rate)
        billing_rates.append(billing_rate)
    
    session.flush()
    
    # Create capacity calendar entries
    for user in users:
        for i in range(-30, 31):  # 30 days back and 30 days forward
            calendar_date = date.today() + timedelta(days=i)
            # Skip weekends
            if calendar_date.weekday() < 5:
                capacity = CapacityCalendar(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    date=calendar_date,
                    capacity_hours=8.0 if calendar_date.weekday() < 5 else 0
                )
                session.add(capacity)
    
    # Create time entries for completed and in-progress tasks
    time_entries = []
    for task in tasks:
        if task.status in ['Done', 'In Progress'] and task.assignee_id:
            # Create multiple time entries for this task
            entry_dates = []
            if task.status == 'Done':
                # Spread entries over past days
                for i in range(1, 6):
                    entry_dates.append(date.today() - timedelta(days=i))
            else:
                # Current work
                entry_dates = [date.today() - timedelta(days=1), date.today()]
            
            for entry_date in entry_dates:
                if entry_date.weekday() < 5:  # Only weekdays
                    minutes = 120 + (hash(str(task.id) + str(entry_date)) % 300)  # 2-7 hours
                    time_entry = TimeEntry(
                        tenant_id=tenant.id,
                        user_id=task.assignee_id,
                        task_id=task.id,
                        entry_date=entry_date,
                        minutes=minutes,
                        billable=True,
                        note=f"Working on {task.title}"
                    )
                    session.add(time_entry)
                    time_entries.append(time_entry)
    
    # Create timesheets
    timesheets = []
    for user in users:
        for week_offset in range(-4, 1):  # Last 4 weeks
            week_start = date.today() - timedelta(days=date.today().weekday()) + timedelta(weeks=week_offset)
            timesheet = Timesheet(
                tenant_id=tenant.id,
                user_id=user.id,
                week_start_date=week_start,
                status='approved' if week_offset < 0 else 'submitted',
                submitted_at=datetime.now() - timedelta(days=-week_offset * 7 + 1) if week_offset < 0 else datetime.now(),
                approved_at=datetime.now() - timedelta(days=-week_offset * 7) if week_offset < -1 else None,
                approved_by_user_id=context['admin_user'].id if week_offset < -1 else None
            )
            session.add(timesheet)
            timesheets.append(timesheet)
    
    session.commit()
    print(f"Created {len(billing_rates)} billing rates, {len(time_entries)} time entries, and {len(timesheets)} timesheets")
    return time_entries, timesheets

def create_sample_integrations(session, context):
    """Create sample integration providers and connections"""
    tenant = context['tenant']
    admin_user = context['admin_user']
    
    # Check if integration providers already exist
    existing_providers = session.query(IntegrationProvider).all()
    if existing_providers:
        print(f"Found {len(existing_providers)} existing integration providers, skipping creation")
        providers = existing_providers
    else:
        # Create integration providers
        providers_data = [
            ('slack', 'Slack', 'Team communication and notifications', 'https://slack.com/favicon.ico'),
            ('github', 'GitHub', 'Source code management and version control', 'https://github.com/favicon.ico'),
            ('jira', 'Jira', 'Issue tracking and project management', 'https://www.atlassian.com/favicon.ico'),
            ('gcal', 'Google Calendar', 'Calendar integration and scheduling', 'https://calendar.google.com/favicon.ico'),
            ('teams', 'Microsoft Teams', 'Team collaboration and meetings', 'https://teams.microsoft.com/favicon.ico')
        ]
        
        providers = []
        for key, name, desc, icon in providers_data:
            provider = IntegrationProvider(
                key=key,
                display_name=name,
                description=desc,
                icon_url=icon,
                is_active=True
            )
            session.add(provider)
            providers.append(provider)
        
        session.flush()
    
    # Create OAuth tokens (simulated)
    oauth_tokens = []
    for provider in providers[:3]:  # First 3 providers
        token = OAuthToken(
            tenant_id=tenant.id,
            user_id=admin_user.id,
            provider_key=provider.key,
            account_label=f"{admin_user.profile.first_name}'s {provider.display_name}",
            access_token_enc="encrypted_access_token_placeholder",
            refresh_token_enc="encrypted_refresh_token_placeholder",
            scopes=['read', 'write'],
            expires_at=datetime.now() + timedelta(days=30)
        )
        session.add(token)
        oauth_tokens.append(token)
    
    # Create integration subscriptions
    subscriptions = []
    for i, provider in enumerate(providers):
        if i < 3:  # Active subscriptions for first 3
            subscription = IntegrationSubscription(
                tenant_id=tenant.id,
                provider_key=provider.key,
                external_id=f"ext_{provider.key}_{tenant.id}",
                config_json=json.dumps({
                    'webhook_url': f'https://api.planora.com/webhooks/{provider.key}',
                    'events': ['task.created', 'task.updated', 'project.created']
                }),
                is_active=True,
                created_by_user_id=admin_user.id
            )
            session.add(subscription)
            subscriptions.append(subscription)
    
    # Create webhook endpoints
    webhook_endpoints = []
    for provider in providers[:2]:
        endpoint = WebhookEndpoint(
            tenant_id=tenant.id,
            provider_key=provider.key,
            endpoint_url=f"https://hooks.{provider.key}.com/planora/{tenant.id}",
            secret="webhook_secret_placeholder",
            event_types=['task.created', 'task.updated', 'comment.created'],
            is_active=True,
            created_by_user_id=admin_user.id
        )
        session.add(endpoint)
        webhook_endpoints.append(endpoint)
    
    session.commit()
    print(f"Created {len(providers)} integration providers with {len(oauth_tokens)} tokens and {len(subscriptions)} subscriptions")
    return providers, oauth_tokens, subscriptions

def create_sample_automation(session, context, tasks):
    """Create sample automation rules and webhooks"""
    tenant = context['tenant']
    admin_user = context['admin_user']
    
    # Create automation rules
    automation_rules_data = [
        {
            'name': 'Auto-assign bugs to lead developer',
            'description': 'Automatically assign new bugs to the lead developer',
            'trigger': 'task.created',
            'condition': {'type': 'bug'},
            'action': {'assign_to': 'developer@planora.com', 'add_label': 'needs-review'}
        },
        {
            'name': 'Notify on high priority tasks',
            'description': 'Send Slack notification for high priority tasks',
            'trigger': 'task.updated',
            'condition': {'priority': 'high', 'status_changed': True},
            'action': {'notify_slack': '#dev-team', 'assign_watcher': 'pm@planora.com'}
        },
        {
            'name': 'Move completed tasks to Done column',
            'description': 'Automatically move tasks to Done when marked complete',
            'trigger': 'task.status_changed',
            'condition': {'status': 'Done'},
            'action': {'move_to_column': 'Done', 'log_completion_time': True}
        },
        {
            'name': 'Create follow-up tasks for epics',
            'description': 'Create follow-up tasks when epic is completed',
            'trigger': 'task.completed',
            'condition': {'type': 'epic'},
            'action': {'create_task': 'Epic Review', 'assign_to_reporter': True}
        }
    ]
    
    automation_rules = []
    for rule_data in automation_rules_data:
        rule = AutomationRule(
            tenant_id=tenant.id,
            name=rule_data['name'],
            description=rule_data['description'],
            trigger=rule_data['trigger'],
            condition_json=json.dumps(rule_data['condition']),
            action_json=json.dumps(rule_data['action']),
            is_enabled=True,
            created_by_user_id=admin_user.id
        )
        session.add(rule)
        automation_rules.append(rule)
    
    session.flush()
    
    # Create automation versions
    for rule in automation_rules:
        version = AutomationVersion(
            rule_id=rule.id,
            version_number=1,
            trigger=rule.trigger,
            condition_json=rule.condition_json,
            action_json=rule.action_json
        )
        session.add(version)
    
    # Create automation runs (execution history)
    automation_runs = []
    for rule in automation_rules:
        for i in range(3):  # 3 runs per rule
            run = AutomationRun(
                rule_id=rule.id,
                tenant_id=tenant.id,
                trigger_data=json.dumps({'task_id': str(tasks[i].id), 'action': 'status_change'}),
                status='success',
                started_at=datetime.now() - timedelta(hours=i*8),
                finished_at=datetime.now() - timedelta(hours=i*8) + timedelta(minutes=2),
                log=f"Rule executed successfully for task {tasks[i].key}"
            )
            session.add(run)
            automation_runs.append(run)
    
    # Create webhooks
    webhooks_data = [
        {
            'name': 'Slack Notifications',
            'target_url': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
            'event_keys': ['task.created', 'task.updated', 'task.completed']
        },
        {
            'name': 'GitHub Integration',
            'target_url': 'https://api.github.com/repos/company/project/hooks',
            'event_keys': ['task.created', 'task.assigned']
        },
        {
            'name': 'Custom Dashboard',
            'target_url': 'https://dashboard.company.com/api/webhooks/planora',
            'event_keys': ['project.created', 'sprint.started', 'sprint.completed']
        }
    ]
    
    webhooks = []
    for webhook_data in webhooks_data:
        webhook = Webhook(
            tenant_id=tenant.id,
            name=webhook_data['name'],
            target_url=webhook_data['target_url'],
            secret='webhook_secret_12345',
            event_keys=webhook_data['event_keys'],
            is_active=True,
            created_by_user_id=admin_user.id
        )
        session.add(webhook)
        webhooks.append(webhook)
    
    session.flush()
    
    # Create webhook deliveries
    webhook_deliveries = []
    for webhook in webhooks:
        for i, event_type in enumerate(webhook.event_keys):
            delivery = WebhookDelivery(
                webhook_id=webhook.id,
                event_type=event_type,
                payload=json.dumps({
                    'event_type': event_type,
                    'timestamp': datetime.now().isoformat(),
                    'data': {'task_id': str(tasks[i].id) if i < len(tasks) else str(tasks[0].id)}
                }),
                response_status=200,
                response_body='OK',
                delivered_at=datetime.now() - timedelta(minutes=i*30),
                retry_count=0
            )
            session.add(delivery)
            webhook_deliveries.append(delivery)
    
    session.commit()
    print(f"Created {len(automation_rules)} automation rules, {len(automation_runs)} runs, and {len(webhooks)} webhooks")
    return automation_rules, webhooks

def create_sample_reports(session, context, projects, tasks):
    """Create sample reports and analytics data"""
    tenant = context['tenant']
    admin_user = context['admin_user']
    pm_user = context['pm_user']
    
    # Create reports
    reports_data = [
        {
            'name': 'Team Velocity Report',
            'description': 'Track team velocity over sprints',
            'type': 'velocity',
            'owner': pm_user,
            'definition': {
                'chart_type': 'line',
                'metrics': ['story_points_completed', 'story_points_committed'],
                'groupby': 'sprint',
                'filters': {'project_id': str(projects[0].id)}
            }
        },
        {
            'name': 'Burndown Chart',
            'description': 'Sprint burndown tracking',
            'type': 'burndown',
            'owner': pm_user,
            'definition': {
                'chart_type': 'area',
                'metrics': ['remaining_work', 'ideal_burndown'],
                'groupby': 'day',
                'filters': {'sprint_active': True}
            }
        },
        {
            'name': 'Task Status Distribution',
            'description': 'Distribution of tasks by status across projects',
            'type': 'custom',
            'owner': admin_user,
            'definition': {
                'chart_type': 'pie',
                'metrics': ['task_count'],
                'groupby': 'status',
                'filters': {}
            }
        },
        {
            'name': 'Time Tracking Summary',
            'description': 'Time spent by team members',
            'type': 'custom',
            'owner': admin_user,
            'definition': {
                'chart_type': 'bar',
                'metrics': ['hours_logged'],
                'groupby': 'user',
                'filters': {'date_range': '30d'}
            }
        },
        {
            'name': 'Project Health Dashboard',
            'description': 'Overall project health metrics',
            'type': 'custom',
            'owner': pm_user,
            'definition': {
                'chart_type': 'dashboard',
                'metrics': ['on_time_delivery', 'budget_utilization', 'team_capacity'],
                'groupby': 'project',
                'filters': {'status': 'active'}
            }
        }
    ]
    
    reports = []
    for report_data in reports_data:
        report = Report(
            tenant_id=tenant.id,
            name=report_data['name'],
            description=report_data['description'],
            definition_json=json.dumps(report_data['definition']),
            report_type=report_data['type'],
            owner_user_id=report_data['owner'].id,
            is_public=True
        )
        session.add(report)
        reports.append(report)
    
    session.flush()
    
    # Create report jobs (execution history)
    report_jobs = []
    for report in reports:
        for i in range(3):
            job = ReportJob(
                report_id=report.id,
                requested_by_user_id=report.owner_user_id,
                status='completed',
                parameters=json.dumps({'date_range': '30d', 'format': 'json'}),
                result_data=json.dumps({
                    'data': [{'x': f'Week {i+1}', 'y': (i+1)*10} for i in range(4)],
                    'summary': {'total_records': 100 + i*50}
                }),
                started_at=datetime.now() - timedelta(days=i*7),
                finished_at=datetime.now() - timedelta(days=i*7) + timedelta(minutes=5)
            )
            session.add(job)
            report_jobs.append(job)
    
    # Create report schedules
    report_schedules = []
    for i, report in enumerate(reports[:3]):  # Schedule first 3 reports
        schedule = ReportSchedule(
            report_id=report.id,
            name=f"Weekly {report.name}",
            cron_expression='0 9 * * MON',  # Monday 9 AM
            recipients=json.dumps(['pm@planora.com', 'admin@planora.com']),
            delivery_format='pdf',
            is_active=True,
            last_run_at=datetime.now() - timedelta(days=7),
            next_run_at=datetime.now() + timedelta(days=7-(datetime.now().weekday())),
            created_by_user_id=report.owner_user_id
        )
        session.add(schedule)
        report_schedules.append(schedule)
    
    # Create dashboards
    dashboard = Dashboard(
        tenant_id=tenant.id,
        name='Executive Dashboard',
        description='High-level overview for executives',
        layout_json=json.dumps({
            'layout': [
                {'i': 'velocity', 'x': 0, 'y': 0, 'w': 6, 'h': 4},
                {'i': 'burndown', 'x': 6, 'y': 0, 'w': 6, 'h': 4},
                {'i': 'status', 'x': 0, 'y': 4, 'w': 4, 'h': 3},
                {'i': 'time', 'x': 4, 'y': 4, 'w': 8, 'h': 3}
            ]
        }),
        owner_user_id=admin_user.id,
        is_public=True
    )
    session.add(dashboard)
    session.flush()
    
    # Create dashboard widgets
    widgets_data = [
        {'type': 'chart', 'title': 'Team Velocity', 'config': {'report_id': str(reports[0].id)}},
        {'type': 'chart', 'title': 'Sprint Burndown', 'config': {'report_id': str(reports[1].id)}},
        {'type': 'metric', 'title': 'Active Tasks', 'config': {'metric': 'active_task_count'}},
        {'type': 'list', 'title': 'Recent Activity', 'config': {'entity': 'recent_tasks', 'limit': 10}}
    ]
    
    for i, widget_data in enumerate(widgets_data):
        widget = DashboardWidget(
            dashboard_id=dashboard.id,
            widget_type=widget_data['type'],
            title=widget_data['title'],
            config_json=json.dumps(widget_data['config']),
            position_x=i % 2 * 6,
            position_y=i // 2 * 4,
            width=6,
            height=4
        )
        session.add(widget)
    
    # Create metrics store entries
    metrics_entries = []
    for project in projects:
        for week in range(4):
            # Velocity metrics
            velocity_entry = MetricsStore(
                tenant_id=tenant.id,
                metric_type='velocity',
                entity_type='project',
                entity_id=str(project.id),
                period_start=datetime.now() - timedelta(weeks=week+1),
                period_end=datetime.now() - timedelta(weeks=week),
                value=json.dumps({
                    'story_points_completed': 25 + week*5,
                    'story_points_committed': 30 + week*3,
                    'tasks_completed': 8 + week*2
                })
            )
            session.add(velocity_entry)
            metrics_entries.append(velocity_entry)
    
    # Create analytics events
    analytics_events = []
    event_types = ['task.created', 'task.updated', 'task.completed', 'project.viewed', 'report.generated']
    
    for i in range(100):  # 100 sample events
        event = AnalyticsEvent(
            tenant_id=tenant.id,
            user_id=context['users'][i % len(context['users'])].id,
            event_type=event_types[i % len(event_types)],
            entity_type='task' if 'task' in event_types[i % len(event_types)] else 'project',
            entity_id=str(tasks[i % len(tasks)].id) if tasks else str(projects[i % len(projects)].id),
            properties=json.dumps({
                'source': 'web_ui',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'session_id': f'session_{i//10}'
            }),
            occurred_at=datetime.now() - timedelta(hours=i//4)
        )
        session.add(event)
        analytics_events.append(event)
    
    # Create saved filters
    saved_filters_data = [
        {
            'name': 'My Active Tasks',
            'entity_type': 'task',
            'filter': {'assignee': 'current_user', 'status': ['To Do', 'In Progress']},
            'owner': pm_user
        },
        {
            'name': 'High Priority Bugs',
            'entity_type': 'task',
            'filter': {'type': 'bug', 'priority': 'high', 'status': ['To Do', 'In Progress']},
            'owner': admin_user
        },
        {
            'name': 'Active Projects',
            'entity_type': 'project',
            'filter': {'status': 'active'},
            'owner': pm_user
        }
    ]
    
    saved_filters = []
    for filter_data in saved_filters_data:
        saved_filter = SavedFilter(
            tenant_id=tenant.id,
            name=filter_data['name'],
            entity_type=filter_data['entity_type'],
            filter_json=json.dumps(filter_data['filter']),
            owner_user_id=filter_data['owner'].id,
            is_public=True
        )
        session.add(saved_filter)
        saved_filters.append(saved_filter)
    
    session.commit()
    print(f"Created {len(reports)} reports, 1 dashboard with 4 widgets, {len(metrics_entries)} metrics entries, {len(analytics_events)} events, and {len(saved_filters)} filters")
    return reports, report_jobs, dashboard

def main():
    """Main function to create comprehensive sample data"""
    print("Creating comprehensive sample data for Planora API...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Get context
        context = get_sample_data_context(session)
        if not context:
            return False
        
        print(f"\n[OK] Found tenant: {context['tenant'].name}")
        print(f"[OK] Found {len(context['users'])} users")
        
        print("\n1. Creating sample projects...")
        projects = create_sample_projects(session, context)
        
        print("\n2. Creating boards and sprints...")
        boards, sprints = create_sample_boards_and_sprints(session, context, projects)
        
        print("\n3. Creating sample tasks...")
        tasks = create_sample_tasks(session, context, projects, sprints)
        
        print("\n4. Creating time tracking data...")
        time_entries, timesheets = create_sample_time_tracking(session, context, tasks)
        
        print("\n5. Creating integration data...")
        providers, oauth_tokens, subscriptions = create_sample_integrations(session, context)
        
        print("\n6. Creating automation rules...")
        automation_rules, webhooks = create_sample_automation(session, context, tasks)
        
        print("\n7. Creating reports and analytics...")
        reports, report_jobs, dashboard = create_sample_reports(session, context, projects, tasks)
        
        print(f"\n[SUCCESS] Comprehensive sample data creation completed!")
        print(f"\nSummary:")
        print(f"  - {len(projects)} Projects")
        print(f"  - {len(tasks)} Tasks") 
        print(f"  - {len(sprints)} Sprints")
        print(f"  - {len(time_entries)} Time Entries")
        print(f"  - {len(providers)} Integration Providers")
        print(f"  - {len(automation_rules)} Automation Rules")
        print(f"  - {len(reports)} Reports")
        print(f"  - 1 Dashboard with widgets")
        print(f"\nYou can now explore the full functionality of the Planora API!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

if __name__ == "__main__":
    main()