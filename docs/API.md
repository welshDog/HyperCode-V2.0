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
*   **Body**:
    ```json
    {
      "title": "Task Title",
      "description": "Code content or instruction",
      "priority": "high",
      "type": "translate", // translate, health, research
      "project_id": 1
    }
    ```
*   **Response**: Returns the created Task object with ID.

#### Get Tasks
*   **GET** `/tasks/`
*   **Query Params**: `skip`, `limit`

### Auth

#### Login
*   **POST** `/login/access-token`
*   **Body**: `username` (email), `password`
*   **Response**: `access_token` (JWT)

## Authentication
All protected endpoints require a Bearer Token in the header:
`Authorization: Bearer <your_token>`
