import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.features.customers.models import Customer
from app.db.database import Base
from datetime import datetime, timedelta
import uuid

def insert_customer_data():
    """Insert mock customer data"""

    # Get database session
    db = SessionLocal()

    try:
        print("Inserting customer data...")

        customers_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "TechCorp Solutions",
                "industry": "Technology",
                "contact": {
                    "name": "John Smith",
                    "email": "john.smith@techcorp.com",
                    "phone": "+1 (555) 123-4567",
                    "title": "CTO"
                },
                "website": "www.techcorp.com",
                "address": {
                    "street": "123 Tech Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                    "country": "USA"
                },
                "status": "Active",
                "join_date": datetime(2023, 1, 15),
                "last_activity": datetime(2024, 12, 20),
                "total_revenue": 250000.0,
                "project_ids": ["PROJ-001", "PROJ-002"],
                "priority": "High",
                "notes": "Key enterprise client with multiple ongoing projects"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Global Finance Inc",
                "industry": "Finance",
                "contact": {
                    "name": "Sarah Johnson",
                    "email": "sarah.johnson@globalfinance.com",
                    "phone": "+1 (555) 234-5678",
                    "title": "Head of IT"
                },
                "website": "www.globalfinance.com",
                "address": {
                    "street": "456 Wall Street",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10005",
                    "country": "USA"
                },
                "status": "Active",
                "join_date": datetime(2023, 3, 10),
                "last_activity": datetime(2024, 12, 19),
                "total_revenue": 500000.0,
                "project_ids": ["PROJ-003"],
                "priority": "Critical",
                "notes": "Large financial institution, high security requirements"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "HealthPlus Medical",
                "industry": "Healthcare",
                "contact": {
                    "name": "Dr. Michael Chen",
                    "email": "michael.chen@healthplus.com",
                    "phone": "+1 (555) 345-6789",
                    "title": "Chief Medical Officer"
                },
                "website": "www.healthplus.com",
                "address": {
                    "street": "789 Medical Center Dr",
                    "city": "Boston",
                    "state": "MA",
                    "zip": "02115",
                    "country": "USA"
                },
                "status": "Active",
                "join_date": datetime(2023, 6, 22),
                "last_activity": datetime(2024, 12, 18),
                "total_revenue": 320000.0,
                "project_ids": ["PROJ-005"],
                "priority": "High",
                "notes": "Healthcare technology modernization project"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Data Insights Ltd",
                "industry": "Analytics",
                "contact": {
                    "name": "Jennifer Taylor",
                    "email": "jennifer.taylor@datainsights.com",
                    "phone": "+1 (555) 456-7890",
                    "title": "Head of Product"
                },
                "website": "www.datainsights.com",
                "address": {
                    "street": "321 Analytics Way",
                    "city": "Austin",
                    "state": "TX",
                    "zip": "78701",
                    "country": "USA"
                },
                "status": "Inactive",
                "join_date": datetime(2023, 5, 18),
                "last_activity": datetime(2024, 12, 20),
                "total_revenue": 180000.0,
                "project_ids": ["PROJ-004"],
                "priority": "Low",
                "notes": "Project on hold due to budget constraints"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "EduTech Academy",
                "industry": "Education",
                "contact": {
                    "name": "Professor David Williams",
                    "email": "david.williams@edutech.edu",
                    "phone": "+1 (555) 567-8901",
                    "title": "Director of Technology"
                },
                "website": "www.edutech.edu",
                "address": {
                    "street": "555 University Ave",
                    "city": "Seattle",
                    "state": "WA",
                    "zip": "98105",
                    "country": "USA"
                },
                "status": "Prospect",
                "join_date": datetime(2024, 1, 12),
                "last_activity": datetime(2024, 12, 15),
                "total_revenue": 0.0,
                "project_ids": [],
                "priority": "Medium",
                "notes": "Potential client for e-learning platform development"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "RetailMax Corporation",
                "industry": "E-commerce",
                "contact": {
                    "name": "Lisa Rodriguez",
                    "email": "lisa.rodriguez@retailmax.com",
                    "phone": "+1 (555) 678-9012",
                    "title": "VP of Digital Transformation"
                },
                "website": "www.retailmax.com",
                "address": {
                    "street": "999 Commerce Blvd",
                    "city": "Chicago",
                    "state": "IL",
                    "zip": "60601",
                    "country": "USA"
                },
                "status": "Active",
                "join_date": datetime(2023, 8, 5),
                "last_activity": datetime(2024, 12, 21),
                "total_revenue": 450000.0,
                "project_ids": ["PROJ-006", "PROJ-007"],
                "priority": "High",
                "notes": "Multi-phase digital transformation initiative"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "GreenEnergy Solutions",
                "industry": "Energy",
                "contact": {
                    "name": "Robert Martinez",
                    "email": "robert.martinez@greenenergy.com",
                    "phone": "+1 (555) 789-0123",
                    "title": "Chief Innovation Officer"
                },
                "website": "www.greenenergy.com",
                "address": {
                    "street": "777 Renewable Way",
                    "city": "Denver",
                    "state": "CO",
                    "zip": "80202",
                    "country": "USA"
                },
                "status": "Active",
                "join_date": datetime(2023, 11, 30),
                "last_activity": datetime(2024, 12, 17),
                "total_revenue": 280000.0,
                "project_ids": ["PROJ-008"],
                "priority": "Medium",
                "notes": "Smart grid monitoring system development"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "MediaStream Pro",
                "industry": "Media & Entertainment",
                "contact": {
                    "name": "Amanda Foster",
                    "email": "amanda.foster@mediastream.com",
                    "phone": "+1 (555) 890-1234",
                    "title": "Technical Director"
                },
                "website": "www.mediastream.com",
                "address": {
                    "street": "888 Entertainment Ave",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip": "90028",
                    "country": "USA"
                },
                "status": "Active",
                "join_date": datetime(2024, 2, 14),
                "last_activity": datetime(2024, 12, 22),
                "total_revenue": 120000.0,
                "project_ids": ["PROJ-009"],
                "priority": "Medium",
                "notes": "Video streaming platform optimization project"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AutoMotive Dynamics",
                "industry": "Automotive",
                "contact": {
                    "name": "Thomas Anderson",
                    "email": "thomas.anderson@automotive.com",
                    "phone": "+1 (555) 901-2345",
                    "title": "Head of Software Engineering"
                },
                "website": "www.automotivedynamics.com",
                "address": {
                    "street": "111 Motor Parkway",
                    "city": "Detroit",
                    "state": "MI",
                    "zip": "48201",
                    "country": "USA"
                },
                "status": "Prospect",
                "join_date": datetime(2024, 3, 8),
                "last_activity": datetime(2024, 12, 10),
                "total_revenue": 0.0,
                "project_ids": [],
                "priority": "High",
                "notes": "Interested in connected vehicle platform development"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "TravelHub International",
                "industry": "Travel & Tourism",
                "contact": {
                    "name": "Maria Gonzalez",
                    "email": "maria.gonzalez@travelhub.com",
                    "phone": "+1 (555) 012-3456",
                    "title": "CTO"
                },
                "website": "www.travelhub.com",
                "address": {
                    "street": "222 Travel Plaza",
                    "city": "Miami",
                    "state": "FL",
                    "zip": "33101",
                    "country": "USA"
                },
                "status": "Inactive",
                "join_date": datetime(2023, 7, 25),
                "last_activity": datetime(2024, 11, 30),
                "total_revenue": 95000.0,
                "project_ids": ["PROJ-010"],
                "priority": "Low",
                "notes": "Travel booking platform - project completed"
            }
        ]

        for customer_data in customers_data:
            # Check if customer already exists
            existing = db.query(Customer).filter(Customer.id == customer_data["id"]).first()
            if not existing:
                db_customer = Customer(**customer_data)
                db.add(db_customer)

        db.commit()
        print(f"[SUCCESS] Inserted {len(customers_data)} customers")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_customer_data()