# API Reference

The HyperCode Core API is built with FastAPI and follows RESTful principles.

## Base URL
`http://localhost:8000/api/v1`

## Interactive Documentation
Swagger UI is available at: `http://localhost:8000/docs`

## Key Endpoints

### Tasks

#### Create Task
*   **POST** `/tasks/`
*   **Auth**: Bearer token required
*   **Body**:
    ```json
    {
      "title": "Task Title",
      "description": "Code content or instruction",
      "priority": "high",
      "type": "translate",
      "project_id": 1
    }
    ```
*   **Response**: Returns the created Task object with ID.

#### Get Tasks
*   **GET** `/tasks/`
*   **Query Params**: `skip`, `limit`
*   **Auth**: Bearer token required

### Auth

#### Login
*   **POST** `/auth/login/access-token`
*   **Body**: `application/x-www-form-urlencoded` with `username` (email) and `password`
*   **Response**: `access_token` (JWT) and `token_type`

Example:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "username=admin@hypercode.ai&password=adminpassword"
```

## Authentication
Most endpoints require a Bearer token in the header:
`Authorization: Bearer <your_token>`
