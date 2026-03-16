"""Unit tests for core API endpoints."""

import pytest
from fastapi import status
from app.core.config import settings


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] in {"ok", "healthy"}
    
    def test_health_check_response_structure(self, client):
        """Test health check response has required fields."""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "service", "version", "environment"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestAPIEndpoints:
    """Tests for core API endpoints."""
    
    def test_root_redirect(self, client):
        """Test root endpoint returns a welcome payload."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_api_docs_accessible(self, client):
        """Test API documentation is accessible."""
        response = client.get(f"{settings.API_V1_STR}/docs")
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
            f"{settings.API_V1_STR}/auth/login/access-token",
            json={"invalid": "data"}
        )
        assert response.status_code in {
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        }


class TestCORSHeaders:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are included in responses."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8088",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access-control-allow-origin" in {k.lower() for k in response.headers.keys()}


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
    f"{settings.API_V1_STR}/docs",
    "/openapi.json",
])
def test_public_endpoints_accessible(client, endpoint):
    """Test that public endpoints are accessible."""
    response = client.get(endpoint)
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_307_TEMPORARY_REDIRECT
    ]
