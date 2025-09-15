import pytest
from fastapi.testclient import TestClient
from app.models import Project, ProjectMember


def test_create_project(client: TestClient, admin_auth_headers):
    """Test creating a new project"""
    response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "TEST",
            "name": "Test Project",
            "description": "A test project for testing",
            "status": "active"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "TEST"
    assert data["name"] == "Test Project"
    assert data["status"] == "active"
    assert "id" in data


def test_create_project_duplicate_key(client: TestClient, admin_auth_headers):
    """Test creating project with duplicate key"""
    # Create first project
    client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "DUP",
            "name": "First Project"
        }
    )
    
    # Try to create second project with same key
    response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "DUP",
            "name": "Second Project"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]["message"]


def test_list_projects(client: TestClient, auth_headers, admin_auth_headers):
    """Test listing projects"""
    # Create a project first
    project_response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "LIST",
            "name": "List Test Project"
        }
    )
    assert project_response.status_code == 200
    
    # List projects
    response = client.get("/api/v1/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] >= 1


def test_get_project(client: TestClient, admin_auth_headers):
    """Test getting project details"""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "GET",
            "name": "Get Test Project"
        }
    )
    project_id = create_response.json()["id"]
    
    # Get project details
    response = client.get(f"/api/v1/projects/{project_id}", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["key"] == "GET"
    assert data["name"] == "Get Test Project"


def test_get_nonexistent_project(client: TestClient, auth_headers):
    """Test getting nonexistent project"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/projects/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


def test_update_project(client: TestClient, admin_auth_headers):
    """Test updating project"""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "UPD",
            "name": "Update Test Project"
        }
    )
    project_id = create_response.json()["id"]
    
    # Update project
    response = client.put(
        f"/api/v1/projects/{project_id}",
        headers=admin_auth_headers,
        json={
            "name": "Updated Project Name",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project Name"
    assert data["description"] == "Updated description"
    assert data["key"] == "UPD"  # Should remain unchanged


def test_delete_project(client: TestClient, admin_auth_headers):
    """Test deleting project"""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "DEL",
            "name": "Delete Test Project"
        }
    )
    project_id = create_response.json()["id"]
    
    # Delete project
    response = client.delete(f"/api/v1/projects/{project_id}", headers=admin_auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
    
    # Verify project is deleted
    get_response = client.get(f"/api/v1/projects/{project_id}", headers=admin_auth_headers)
    assert get_response.status_code == 404


def test_list_project_members(client: TestClient, admin_auth_headers):
    """Test listing project members"""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "MEM",
            "name": "Members Test Project"
        }
    )
    project_id = create_response.json()["id"]
    
    # List members
    response = client.get(f"/api/v1/projects/{project_id}/members", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Should have at least the owner


def test_project_search(client: TestClient, admin_auth_headers):
    """Test project search functionality"""
    # Create projects with different names
    client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "SEARCH1",
            "name": "Marketing Campaign Project"
        }
    )
    client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "SEARCH2",
            "name": "Development Sprint Project"
        }
    )
    
    # Search for marketing projects
    response = client.get(
        "/api/v1/projects?search=marketing",
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # Check that returned projects contain the search term
    found_marketing = any(
        "marketing" in project["name"].lower()
        for project in data["projects"]
    )
    assert found_marketing


def test_project_status_filter(client: TestClient, admin_auth_headers):
    """Test filtering projects by status"""
    # Create active project
    client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "ACTIVE",
            "name": "Active Project",
            "status": "active"
        }
    )
    
    # Create archived project
    archived_response = client.post(
        "/api/v1/projects",
        headers=admin_auth_headers,
        json={
            "key": "ARCH",
            "name": "Archived Project",
            "status": "archived"
        }
    )
    
    # Filter by active status
    response = client.get(
        "/api/v1/projects?status=active",
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # All returned projects should be active
    assert all(project["status"] == "active" for project in data["projects"])


def test_unauthorized_project_access(client: TestClient):
    """Test accessing projects without authentication"""
    response = client.get("/api/v1/projects")
    assert response.status_code == 401