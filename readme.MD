# Simple Rest Web Service with Flask-RESTx API 

## Overview

This is a sample REST API built using **Flask** and **Flask-RESTx**. The API allows you to manage users and posts, with full support for creating, retrieving, updating, and deleting users and posts. The API is also equipped with detailed error handling (for `404`, `400`, and `500` status codes) and logging to track requests and errors.

## Features

- **Users Resource**: 
  - Get all users
  - Get a single user by ID
  - Create a new user
  - Update an existing user
  - Delete a user
- **Posts Resource**: 
  - Get all posts
  - Get posts for a specific user
  - Create a post for a user
- **HATEOAS Links**: 
  - Retrieve HATEOAS links for a user (self, posts, edit, delete)
- **Error Handling**: 
  - `404`: Resource not found
  - `400`: Bad request (e.g., missing data)
  - `500`: Internal server error
- **Logging**: 
  - All API calls and errors are logged for easier debugging and traceability.

## Installation

1. **Create a virtual environment and activate it**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. The API will run at `http://127.0.0.1:5000/`.

## API Endpoints

### 1. Users

| Method | Endpoint        | Description                |
|--------|-----------------|----------------------------|
| GET    | `/users`         | Retrieve all users         |
| POST   | `/users`         | Create a new user          |
| GET    | `/users/<id>`    | Retrieve a user by ID      |
| PUT    | `/users/<id>`    | Update a user by ID        |
| DELETE | `/users/<id>`    | Delete a user by ID        |

#### Example Requests:

- **Create a new user** (POST `/users`):
  ```json
  {
    "name": "Raufur"
  }
  ```

- **Update a user** (PUT `/users/1`):
  ```json
  {
    "name": "Shimanto"
  }
  ```

### 2. Posts

| Method | Endpoint               | Description                           |
|--------|------------------------|---------------------------------------|
| GET    | `/posts`                | Retrieve all posts                    |
| POST   | `/posts`                | Create a new post                     |
| GET    | `/users/<id>/posts`     | Retrieve all posts for a specific user|
| POST   | `/users/<id>/posts`     | Create a post for a specific user     |

#### Example Requests:

- **Create a new post** (POST `/posts`):
  ```json
  {
    "user_id": 1,
    "title": "My first post"
  }
  ```

- **Create a post for a user** (POST `/users/1/posts`):
  ```json
  {
    "title": "Post title"
  }
  ```

### 3. HATEOAS Links for a User

| Method | Endpoint                 | Description                   |
|--------|--------------------------|-------------------------------|
| GET    | `/users/<id>/links`       | Retrieve HATEOAS links for user|

#### Example Response:

```json
{
  "self": "/users/1",
  "posts": "/users/1/posts",
  "edit": {
    "href": "/users/1",
    "method": "PUT"
  },
  "delete": {
    "href": "/users/1",
    "method": "DELETE"
  }
}
```

## Error Handling

- **404 - Not Found**: Returned when a resource is not found, e.g., requesting a non-existing user.
- **400 - Bad Request**: Returned when the request is malformed or missing required fields.
- **500 - Internal Server Error**: Returned when there is an unexpected error in the server.

Example of a `404` error response:
```json
{
  "message": "Resource not found"
}
```

## Logging

All API requests and errors are logged for monitoring purposes. The logs include:

- **INFO**: For successful operations like fetching or creating resources.
- **WARNING**: For client-side errors like missing required fields (400 errors).
- **ERROR**: For server-side errors or exceptions.

Logs are printed in the console but can be configured to be stored in a file for production environments.

## Requirements

- **Python 3.10+**
- **Flask**
- **Flask-RESTx**
```