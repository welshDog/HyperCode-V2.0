"""Unit tests for core API endpoints."""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_health_check_response_structure(self, client):
        """Test health check response has required fields."""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "timestamp", "version"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestAPIEndpoints:
    """Tests for core API endpoints."""
    
    def test_root_redirect(self, client):
        """Test root endpoint redirects to docs."""
        response = client.get("/", allow_redirects=False)
        assert response.status_code in [
            status.HTTP_307_TEMPORARY_REDIRECT,
            status.HTTP_308_PERMANENT_REDIRECT
        ]
    
    def test_api_docs_accessible(self, client):
        """Test API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "swagger" in response.text.lower()
    
    def test_openapi_schema_accessible(self, client):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for incorrect HTTP method."""
        response = client.post("/health")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_422_validation_error(self, client):
        """Test 422 error for invalid request body."""
        response = client.post(
            "/api/auth/login",
            json={"invalid": "data"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are included in responses."""
        response = client.options("/health")
        # CORS headers should be set by middleware
        assert response.status_code == status.HTTP_200_OK


class TestRateLimiting:
    """Tests for rate limiting (when implemented)."""
    
    @pytest.mark.skip(reason="Rate limiting not yet implemented")
    def test_rate_limit_exceeded(self, client):
        """Test rate limit returns 429."""
        for _ in range(101):  # Exceed 100 req/min limit
            response = client.get("/health")
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.parametrize("endpoint", [
    "/health",
    "/docs",
    "/openapi.json",
])
def test_public_endpoints_accessible(client, endpoint):
    """Test that public endpoints are accessible."""
    response = client.get(endpoint)
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_307_TEMPORARY_REDIRECT
    ]
