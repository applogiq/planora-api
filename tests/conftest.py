import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import get_db, Base
from app.core.config import settings
from app.models import User, Role, Permission, UserRole, RolePermission
from app.core.security import get_password_hash
import uuid


# Create test database
SQLALCHEMY_DATABASE_URL = settings.DATABASE_TEST_URL or "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def setup_test_db():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_test_db):
    """Get database session for testing"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(setup_test_db) -> Generator:
    """Get test client"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_tenant(db_session):
    """Create test tenant"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Organization",
        plan="standard"
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    """Create test user"""
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session, test_tenant):
    """Create admin user with admin role"""
    # Create admin user
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        is_active=True
    )
    db_session.add(user)
    db_session.flush()
    
    # Create admin role with permissions
    admin_role = Role(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        name="Admin",
        description="Administrator role"
    )
    db_session.add(admin_role)
    db_session.flush()
    
    # Create permissions
    permissions = [
        Permission(id=uuid.uuid4(), key="admin.manage", description="Full admin access"),
        Permission(id=uuid.uuid4(), key="project.manage", description="Manage projects"),
        Permission(id=uuid.uuid4(), key="task.create", description="Create tasks"),
        Permission(id=uuid.uuid4(), key="task.update", description="Update tasks"),
        Permission(id=uuid.uuid4(), key="task.delete", description="Delete tasks"),
    ]
    
    for permission in permissions:
        db_session.add(permission)
        db_session.flush()
        
        # Assign permission to admin role
        role_permission = RolePermission(
            role_id=admin_role.id,
            permission_id=permission.id
        )
        db_session.add(role_permission)
    
    # Assign admin role to user
    user_role = UserRole(
        user_id=user.id,
        role_id=admin_role.id
    )
    db_session.add(user_role)
    
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Get authentication headers for admin user"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "email": admin_user.email,
            "password": "adminpassword123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}