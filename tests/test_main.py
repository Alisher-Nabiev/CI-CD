import pytest
import json
from datetime import datetime
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestBasicEndpoints:
    """Test basic application endpoints."""
    
    def test_home(self, client):
        """Test the home endpoint returns correct response."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"Hello from Flask CI/CD!" in response.data

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

    def test_ready_endpoint(self, client):
        """Test the readiness endpoint."""
        response = client.get('/ready')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'ready'
        assert 'uptime_seconds' in data
        assert isinstance(data['uptime_seconds'], (int, float))

    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'uptime_seconds' in data
        assert 'version' in data
        assert 'start_time' in data


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not found'

    def test_method_not_allowed(self, client):
        """Test method not allowed error."""
        response = client.post('/')
        assert response.status_code == 405


class TestResponseHeaders:
    """Test response headers and content types."""
    
    def test_health_content_type(self, client):
        """Test health endpoint returns JSON content type."""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_ready_content_type(self, client):
        """Test ready endpoint returns JSON content type."""
        response = client.get('/ready')
        assert response.content_type == 'application/json'


class TestDataValidation:
    """Test data format and validation."""
    
    def test_health_timestamp_format(self, client):
        """Test health endpoint timestamp is valid ISO format."""
        response = client.get('/health')
        data = json.loads(response.data)
        
        # Should be able to parse as ISO format datetime
        timestamp = data['timestamp']
        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed_time, datetime)

    def test_uptime_is_positive(self, client):
        """Test that uptime is always positive."""
        response = client.get('/ready')
        data = json.loads(response.data)
        
        assert data['uptime_seconds'] >= 0


class TestSecurityHeaders:
    """Test security-related headers and responses."""
    
    def test_no_server_header_leakage(self, client):
        """Test that server information is not leaked."""
        response = client.get('/')
        # Should not expose Flask/Werkzeug version information
        server_header = response.headers.get('Server', '')
        assert 'Flask' not in server_header
        assert 'Werkzeug' not in server_header
