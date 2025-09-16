# Planora API - Project Management System

A comprehensive project management system built with FastAPI and PostgreSQL.

## Features

### Core Modules
1. **User Management** - User CRUD operations, role assignment, profile management
2. **Roles & Access Control** - Permission-based access control system
3. **Authentication** - JWT-based authentication with refresh tokens
4. **Audit Logs** - Complete activity tracking and logging
5. **Project Management** - Project lifecycle management
6. **Task Planning** - Kanban board, sprint management, task tracking

### Additional APIs
- **Dashboard** - Overview statistics and user workload
- **Reports** - Project progress, time tracking, productivity reports
- **Notifications** - System notifications and user alerts

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### Users
- `GET /api/v1/users/` - List all users
- `POST /api/v1/users/` - Create new user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `GET /api/v1/users/active/list` - Get active users
- `GET /api/v1/users/role/{role_name}` - Get users by role

### Roles
- `GET /api/v1/roles/` - List all roles
- `POST /api/v1/roles/` - Create new role
- `GET /api/v1/roles/{role_id}` - Get role by ID
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role
- `GET /api/v1/roles/active/list` - Get active roles
- `GET /api/v1/roles/permissions/list` - Get available permissions

### Projects
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{project_id}` - Get project by ID
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project
- `GET /api/v1/projects/active/list` - Get active projects
- `GET /api/v1/projects/status/{status}` - Get projects by status
- `GET /api/v1/projects/stats/overview` - Get project statistics

### Tasks
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/{task_id}` - Get task by ID
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- `GET /api/v1/tasks/board/kanban` - Get Kanban board view
- `GET /api/v1/tasks/stats/overview` - Get task statistics

### Audit Logs
- `GET /api/v1/audit-logs/` - List audit logs
- `GET /api/v1/audit-logs/{log_id}` - Get audit log by ID
- `GET /api/v1/audit-logs/user/{user_id}` - Get user audit logs
- `GET /api/v1/audit-logs/stats/summary` - Get audit statistics

### Dashboard
- `GET /api/v1/dashboard/overview` - Get dashboard overview
- `GET /api/v1/dashboard/user-workload` - Get user workload
- `GET /api/v1/dashboard/team-performance` - Get team performance

### Reports
- `GET /api/v1/reports/project-progress` - Project progress report
- `GET /api/v1/reports/time-tracking` - Time tracking report
- `GET /api/v1/reports/productivity` - Productivity report
- `GET /api/v1/reports/task-completion` - Task completion report

### Notifications
- `GET /api/v1/notifications/` - Get user notifications
- `POST /api/v1/notifications/{notification_id}/mark-read` - Mark notification as read
- `POST /api/v1/notifications/mark-all-read` - Mark all notifications as read

## Permission System

The system uses a role-based permission system with the following permissions:
- `user:read`, `user:write`, `user:delete` - User management
- `role:read`, `role:write` - Role management
- `project:read`, `project:write`, `project:delete` - Project management
- `task:read`, `task:write`, `task:delete` - Task management
- `team:read`, `team:write` - Team management
- `report:read`, `report:write` - Report access
- `audit:read` - Audit log access
- `*` - Super admin (all permissions)

## Default Users

The system comes with these default users:

### Super Admin
- **Email:** superadmin@planora.com
- **Password:** super123
- **Permissions:** All permissions (*)

### Admin
- **Email:** admin@planora.com
- **Password:** admin123
- **Permissions:** User, role, project, and settings management

### Project Manager
- **Email:** pm@planora.com
- **Password:** pm123
- **Permissions:** Project and task management, team coordination

## Setup Instructions

### Quick Setup (Recommended)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secret key
   ```

3. **Database Setup with Mock Data**
   ```bash
   # Create PostgreSQL database named 'planora_db' first
   python setup_database.py
   ```

4. **Run the Application**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   source venv/bin/activate
   source venv/bin/activate && uvicorn main:app --reload --port 8000   
   uvicorn app.main:app --reload --port 8000
   ```

5. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Alternative Setup Options

**Option 1: Basic setup with minimal data**
```bash
python create_db.py
```

**Option 2: Full mock data setup**
```bash
python insert_mock_data.py
```

**Option 3: Basic setup with mock data flag**
```bash
python create_db.py --with-mock-data
```

### Database Requirements

1. **PostgreSQL Installation**
   - Install PostgreSQL (version 12 or higher)
   - Create a database named `planora_db`
   - Update the DATABASE_URL in your .env file

2. **Environment Variables**
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/planora_db
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── endpoints/          # API route handlers
│       └── api.py             # API router configuration
├── core/
│   ├── config.py              # Application configuration
│   ├── security.py            # Authentication utilities
│   └── deps.py                # Dependency injection
├── crud/                      # Database operations
├── db/
│   ├── database.py            # Database connection
│   └── init_db.py             # Database initialization
├── models/                    # SQLAlchemy models
└── schemas/                   # Pydantic schemas
```

## Technology Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** bcrypt
- **API Documentation:** Swagger/OpenAPI

## Security Features

- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Comprehensive audit logging
- Request/response validation with Pydantic
- CORS middleware configuration