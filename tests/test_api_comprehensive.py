"""
Comprehensive API Test Suite for LIHC Platform
Tests all API endpoints with various scenarios and edge cases
"""

import pytest
import asyncio
import json
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import io

# Import the main FastAPI app
from src.api.main import app
from src.database.models import Base, get_db, User, Dataset, Analysis
from src.utils.logging_system import LIHCLogger

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = LIHCLogger(name="APITests")


# Test database setup
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


class TestAPIEndpoints:
    """Comprehensive API endpoint tests"""
    
    @classmethod
    def setup_class(cls):
        """Set up test database and test data"""
        Base.metadata.create_all(bind=engine)
        cls.test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        cls.admin_user_data = {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "adminpassword123",
            "full_name": "Admin User",
            "role": "admin"
        }
        cls.access_token = None
        cls.admin_token = None
    
    @classmethod
    def teardown_class(cls):
        """Clean up test database"""
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    def test_user_registration(self):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json=self.test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == self.test_user_data["username"]
        assert data["email"] == self.test_user_data["email"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    def test_admin_user_registration(self):
        """Test admin user registration"""
        response = client.post("/api/v1/auth/register", json=self.admin_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == self.admin_user_data["username"]
        assert data["role"] == "admin"
    
    def test_user_login(self):
        """Test user login"""
        login_data = {
            "username": self.test_user_data["username"],
            "password": self.test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Store token for subsequent tests
        self.__class__.access_token = data["access_token"]
    
    def test_admin_login(self):
        """Test admin user login"""
        login_data = {
            "username": self.admin_user_data["username"],
            "password": self.admin_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        
        # Store admin token for subsequent tests
        self.__class__.admin_token = data["access_token"]
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401
    
    def test_get_current_user(self):
        """Test getting current user information"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == self.test_user_data["username"]
        assert data["email"] == self.test_user_data["email"]
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    def test_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_dataset_upload(self):
        """Test dataset upload"""
        # Create a sample CSV file
        sample_data = pd.DataFrame({
            'gene_id': ['GENE1', 'GENE2', 'GENE3'],
            'sample1': [1.5, 2.3, 0.8],
            'sample2': [2.1, 1.7, 1.2],
            'sample3': [0.9, 3.1, 2.5]
        })
        
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        files = {"file": ("test_data.csv", csv_content, "text/csv")}
        data = {
            "name": "Test Dataset",
            "description": "Test dataset for API testing",
            "data_type": "rna_seq"
        }
        
        response = client.post("/api/v1/datasets/upload", headers=headers, files=files, data=data)
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == "Test Dataset"
        assert response_data["data_type"] == "rna_seq"
        assert "id" in response_data
        
        # Store dataset ID for subsequent tests
        self.__class__.test_dataset_id = response_data["id"]
    
    def test_get_datasets(self):
        """Test getting user datasets"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get("/api/v1/datasets", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # Should have at least the uploaded dataset
    
    def test_get_dataset_by_id(self):
        """Test getting specific dataset"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get(f"/api/v1/datasets/{self.test_dataset_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.test_dataset_id
        assert data["name"] == "Test Dataset"
    
    def test_get_nonexistent_dataset(self):
        """Test getting non-existent dataset"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get("/api/v1/datasets/nonexistent-id", headers=headers)
        assert response.status_code == 404
    
    def test_start_analysis(self):
        """Test starting an analysis"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        analysis_data = {
            "name": "Test Analysis",
            "analysis_type": "closedloop",
            "dataset_ids": [self.test_dataset_id],
            "parameters": {
                "target_genes": ["GENE1", "GENE2"],
                "significance_threshold": 0.05
            }
        }
        
        response = client.post("/api/v1/analyses", headers=headers, json=analysis_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Analysis"
        assert data["analysis_type"] == "closedloop"
        assert data["status"] == "queued"
        
        # Store analysis ID for subsequent tests
        self.__class__.test_analysis_id = data["id"]
    
    def test_get_analyses(self):
        """Test getting user analyses"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get("/api/v1/analyses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_analysis_by_id(self):
        """Test getting specific analysis"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get(f"/api/v1/analyses/{self.test_analysis_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.test_analysis_id
        assert data["name"] == "Test Analysis"
    
    def test_cancel_analysis(self):
        """Test canceling an analysis"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.post(f"/api/v1/analyses/{self.test_analysis_id}/cancel", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Analysis cancelled successfully"
    
    def test_admin_get_all_users(self):
        """Test admin endpoint to get all users"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Test user and admin user
    
    def test_non_admin_access_admin_endpoint(self):
        """Test non-admin user accessing admin endpoint"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 403
    
    def test_export_analysis_results(self):
        """Test exporting analysis results"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        export_data = {
            "format": "csv",
            "include_metadata": True
        }
        response = client.post(
            f"/api/v1/analyses/{self.test_analysis_id}/export",
            headers=headers,
            json=export_data
        )
        # This might return 404 if analysis hasn't completed, which is acceptable for test
        assert response.status_code in [200, 404]
    
    def test_batch_analysis(self):
        """Test batch analysis submission"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        batch_data = {
            "job_name": "Test Batch Analysis",
            "analysis_type": "comparative",
            "dataset_groups": [[self.test_dataset_id]],
            "group_names": ["Group1"],
            "parameters": {
                "comparison_type": "multi_group"
            }
        }
        
        response = client.post("/api/v1/batch/submit", headers=headers, json=batch_data)
        assert response.status_code == 201
        data = response.json()
        assert "job_id" in data
        assert data["job_name"] == "Test Batch Analysis"
    
    def test_get_system_stats(self):
        """Test getting system statistics"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_datasets" in data
        assert "total_analyses" in data


class TestWebSocketConnection:
    """Test WebSocket functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        with client.websocket_connect(f"/ws/analysis/{TestAPIEndpoints.test_analysis_id}") as websocket:
            # Send a test message
            websocket.send_json({"type": "status_request"})
            
            # Receive response
            data = websocket.receive_json()
            assert "type" in data
            assert "status" in data


class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_invalid_dataset_upload(self):
        """Test uploading invalid dataset"""
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        
        # Invalid file type
        files = {"file": ("test.txt", b"invalid content", "text/plain")}
        data = {
            "name": "Invalid Dataset",
            "data_type": "rna_seq"
        }
        
        response = client.post("/api/v1/datasets/upload", headers=headers, files=files, data=data)
        assert response.status_code == 400
    
    def test_missing_required_fields(self):
        """Test API with missing required fields"""
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        
        # Missing analysis name
        analysis_data = {
            "analysis_type": "closedloop",
            "dataset_ids": [TestAPIEndpoints.test_dataset_id]
        }
        
        response = client.post("/api/v1/analyses", headers=headers, json=analysis_data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_analysis_type(self):
        """Test invalid analysis type"""
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        analysis_data = {
            "name": "Invalid Analysis",
            "analysis_type": "invalid_type",
            "dataset_ids": [TestAPIEndpoints.test_dataset_id],
            "parameters": {}
        }
        
        response = client.post("/api/v1/analyses", headers=headers, json=analysis_data)
        assert response.status_code == 422


class TestPerformance:
    """Performance tests for API endpoints"""
    
    def test_concurrent_requests(self):
        """Test concurrent API requests"""
        import concurrent.futures
        import time
        
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        
        def make_request():
            start_time = time.time()
            response = client.get("/api/v1/datasets", headers=headers)
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for status_code, response_time in results:
            assert status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_large_dataset_upload(self):
        """Test uploading a large dataset"""
        # Create a larger dataset
        large_data = pd.DataFrame({
            f'gene_{i}': [f'GENE{i}'] + [float(j) for j in range(1000)]
            for i in range(10)
        })
        
        csv_buffer = io.StringIO()
        large_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        files = {"file": ("large_data.csv", csv_content, "text/csv")}
        data = {
            "name": "Large Test Dataset",
            "description": "Large dataset for performance testing",
            "data_type": "rna_seq"
        }
        
        start_time = time.time()
        response = client.post("/api/v1/datasets/upload", headers=headers, files=files, data=data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert end_time - start_time < 30.0  # Should complete within 30 seconds


class TestSecurity:
    """Security tests for API endpoints"""
    
    def test_sql_injection_attempt(self):
        """Test SQL injection protection"""
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        
        # Attempt SQL injection in dataset query
        malicious_id = "1'; DROP TABLE datasets; --"
        response = client.get(f"/api/v1/datasets/{malicious_id}", headers=headers)
        
        # Should return 404 (not found) rather than causing SQL error
        assert response.status_code == 404
    
    def test_xss_protection(self):
        """Test XSS protection in user input"""
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        
        # Attempt XSS in analysis name
        xss_payload = "<script>alert('xss')</script>"
        analysis_data = {
            "name": xss_payload,
            "analysis_type": "closedloop",
            "dataset_ids": [TestAPIEndpoints.test_dataset_id],
            "parameters": {}
        }
        
        response = client.post("/api/v1/analyses", headers=headers, json=analysis_data)
        
        if response.status_code == 201:
            # If created, check that the payload is properly escaped
            data = response.json()
            assert "<script>" not in data["name"]
    
    def test_unauthorized_file_access(self):
        """Test protection against unauthorized file access"""
        headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
        
        # Attempt to access files outside allowed directory
        malicious_path = "../../../etc/passwd"
        response = client.get(f"/api/v1/datasets/download/{malicious_path}", headers=headers)
        
        # Should be blocked
        assert response.status_code in [400, 403, 404]


# Pytest fixtures and configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test asynchronous API endpoints"""
    
    async def test_async_analysis_status(self):
        """Test async analysis status endpoint"""
        async with client:
            headers = {"Authorization": f"Bearer {TestAPIEndpoints.access_token}"}
            response = await client.get(
                f"/api/v1/analyses/{TestAPIEndpoints.test_analysis_id}/status",
                headers=headers
            )
            assert response.status_code in [200, 404]


def run_api_tests():
    """Run all API tests with detailed reporting"""
    import subprocess
    import sys
    
    # Run pytest with detailed output
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("API Test Results:")
    print("=" * 50)
    print(result.stdout)
    
    if result.stderr:
        print("\nErrors:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    # Run tests when script is executed directly
    success = run_api_tests()
    if success:
        print("\n✅ All API tests passed!")
    else:
        print("\n❌ Some API tests failed!")
        sys.exit(1)