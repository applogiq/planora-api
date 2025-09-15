#!/usr/bin/env python3
"""
Debug user registration issue
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core import security
from app.models import User, UserProfile, Role, UserRole
from app.schemas.auth import UserRegister
import uuid

def test_registration():
    """Test user registration logic"""
    print("Testing user registration...")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Simulate registration data
        user_data = UserRegister(
            email="debug@example.com",
            password="DebugPass123",
            first_name="Debug",
            last_name="User"
        )
        
        print(f"Registration data: {user_data}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            print("User already exists, deleting for test...")
            db.delete(existing_user)
            db.commit()
        
        # Get or create tenant
        tenant = db.query(Tenant).first()
        if not tenant:
            print("No tenant found, creating one...")
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Debug Organization"
            )
            db.add(tenant)
            db.flush()
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email=user_data.email,
            password_hash=security.get_password_hash(user_data.password),
            is_active=True
        )
        db.add(user)
        db.flush()
        
        print(f"Created user: {user.email} (ID: {user.id})")
        
        # Create user profile
        if user_data.first_name or user_data.last_name:
            profile = UserProfile(
                id=uuid.uuid4(),
                user_id=user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            db.add(profile)
            print(f"Created profile: {profile.first_name} {profile.last_name}")
        
        # Check for roles
        existing_users_count = db.query(User).filter(User.tenant_id == tenant.id).count()
        print(f"Users in tenant: {existing_users_count}")
        
        if existing_users_count == 1:  # First user becomes admin
            admin_role = db.query(Role).filter(
                Role.tenant_id == tenant.id,
                Role.name == "Admin"
            ).first()
            
            if not admin_role:
                print("Creating admin role...")
                admin_role = Role(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    name="Admin",
                    description="Administrator role with full access"
                )
                db.add(admin_role)
                db.flush()
            
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            db.add(user_role)
            print(f"Assigned admin role to user")
        
        db.commit()
        print("Registration completed successfully!")
        
        # Verify user was created
        created_user = db.query(User).filter(User.email == user_data.email).first()
        if created_user:
            print(f"User verified in database: {created_user.email}")
            
            # Test serialization
            try:
                from app.schemas.user import User as UserSchema
                user_dict = {
                    'id': str(created_user.id),
                    'tenant_id': str(created_user.tenant_id),
                    'email': created_user.email,
                    'is_active': created_user.is_active,
                    'created_at': created_user.created_at,
                    'profile': None
                }
                
                # Get profile if exists
                profile = db.query(UserProfile).filter(UserProfile.user_id == created_user.id).first()
                if profile:
                    user_dict['profile'] = {
                        'id': str(profile.id),
                        'user_id': str(profile.user_id),
                        'first_name': profile.first_name,
                        'last_name': profile.last_name,
                        'avatar_url': profile.avatar_url,
                        'bio': profile.bio,
                        'timezone': profile.timezone
                    }
                
                user_schema = UserSchema(**user_dict)
                print(f"User schema serialization successful: {user_schema.email}")
                return True
                
            except Exception as e:
                print(f"User schema serialization failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("User not found after creation")
            return False
            
    except Exception as e:
        print(f"Registration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_registration()