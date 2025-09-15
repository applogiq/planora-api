# Planora API

A comprehensive project management API built with FastAPI, PostgreSQL, and modern Python best practices.

## Features

- **Multi-tenant Architecture**: Secure tenant isolation with Row-Level Security (RLS)
- **Authentication & Authorization**: JWT tokens, API keys, and role-based access control
- **Project Management**: Projects, tasks, boards, sprints, and custom fields
- **Real-time Collaboration**: WebSocket support for live updates
- **Resource Management**: Time tracking, capacity planning, and reporting
- **Workflow Automation**: Rule-based automation with webhooks
- **Integrations**: Slack, GitHub, calendar sync, and import/export
- **RESTful API**: OpenAPI/Swagger documentation with comprehensive validation

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Search**: OpenSearch for full-text search capabilities
- **Cache**: Redis for caching and real-time features
- **Background Tasks**: Celery with Redis broker
- **Testing**: pytest with async support
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- (Optional) OpenSearch 2.0+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd taskq-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Enable PostgreSQL extensions and initialize database:
```bash
python enable_extensions.py
python init_db.py
```

6. (Optional) Load sample data for testing:
```bash
python sample_data/setup_all_data.py
```

7. Start the development server:
```bash

python -m venv venv
venv\Scripts\activate
source venv/bin/activate
uvicorn app.main:app --reload
# Or use the simplified server:
python simple_server.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Sample Data

The `sample_data/` folder contains scripts to populate the database with realistic test data:

### Quick Setup
```bash
# Create comprehensive sample data (users, projects, tasks, etc.)
python sample_data/setup_all_data.py

# View what sample data exists
python sample_data/list_sample_data.py

# Reset all data (WARNING: deletes everything!)
python sample_data/reset_sample_data.py
```

### Sample Users
After running the sample data setup, you can login with any of these users (password: `Applogiq@123`):
- `admin@planora.com` - Admin role
- `pm@planora.com` - Project Manager role  
- `developer@planora.com` - Developer role
- `designer@planora.com` - Designer role
- `tester@planora.com` - Tester role

### Sample Data Includes
- **8 Users** with different roles and permissions
- **5 Projects** with various statuses and workflows
- **45 Tasks** including epics, stories, and bugs
- **Time tracking** entries and timesheets
- **Integration** configurations (Slack, GitHub, etc.)
- **Automation** rules and webhooks
- **Reports** and analytics dashboards

See `sample_data/README.md` for detailed information.

## Configuration

The application uses environment variables for configuration. Key settings include:

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_TEST_URL`: Test database connection string

### Authentication
- `SECRET_KEY`: JWT signing secret (required)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)

### External Services
- `REDIS_URL`: Redis connection string
- `OPENSEARCH_HOST`: OpenSearch host
- `OPENSEARCH_PORT`: OpenSearch port

### Application
- `DEBUG`: Enable debug mode (default: false)
- `ENVIRONMENT`: Environment name (development/staging/production)
- `ALLOWED_ORIGINS`: CORS allowed origins

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/api-tokens` - Create API token

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project
- `GET /api/v1/projects/{id}/members` - List project members
- `POST /api/v1/projects/{id}/members` - Add project member

### Tasks
- `GET /api/v1/tasks` - List tasks with filtering
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task details
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/{id}/comments` - List task comments
- `POST /api/v1/tasks/{id}/comments` - Create comment
- `GET /api/v1/tasks/{id}/history` - Get task history

## Database Schema

The application uses a comprehensive database schema with the following key entities:

- **Tenants**: Multi-tenant isolation
- **Users**: User accounts with profiles
- **Roles & Permissions**: RBAC system
- **Projects**: Project management
- **Tasks**: Task tracking with hierarchy
- **Comments**: Task discussions
- **Attachments**: File uploads
- **Time Tracking**: Time entries and timesheets
- **Automation**: Workflow rules and webhooks
- **Integrations**: External service connections

## Security Features

- **Row-Level Security (RLS)**: Tenant data isolation at database level
- **JWT Authentication**: Secure token-based authentication
- **API Key Support**: Alternative authentication for integrations
- **Password Security**: bcrypt hashing with salt
- **Rate Limiting**: Configurable rate limits per endpoint
- **Input Validation**: Comprehensive request validation
- **CORS Protection**: Configurable cross-origin policies
- **Security Headers**: Standard security headers included

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Docker
```bash
# Build image
docker build -t planora-api .

# Run container
docker run -p 8000:8000 --env-file .env planora-api
```

### Production Considerations

1. **Database**: Use managed PostgreSQL with read replicas
2. **Cache**: Use managed Redis cluster
3. **File Storage**: Configure S3 or compatible object storage
4. **Monitoring**: Set up logging, metrics, and alerting
5. **Security**: Use HTTPS, secure secrets management
6. **Scaling**: Use load balancer and horizontal scaling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the project scope document for detailed requirements