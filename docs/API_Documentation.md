# API Documentation – Habit & Productivity Analytics API

## 1. Project Overview

Habit & Productivity Analytics API is a data-driven REST API developed for coursework demonstration. It manages two core resources, habit categories and habit records, backed by SQLAlchemy ORM models. The system includes JWT-based authentication for protected write operations, and an analytics endpoint that returns aggregated summary metrics from persisted records. Initial data is derived from a Kaggle 90-day habit tracker dataset and mapped into structured entities. The API is tested with pytest and integrated with a frontend dashboard that consumes real backend responses.

Database configuration is environment-driven: SQLite is used for local development/testing, and PostgreSQL is supported for deployment through `DATABASE_URL` (required when running with production environment settings).

## 2. Base URL

- Local: `http://127.0.0.1:8000`
- Deployed demo: `https://web-service-fuhg.onrender.com`

## 3. Authentication

- **Scheme:** JWT Bearer Token
- **JSON login endpoint (frontend/manual):** `POST /auth/login`
- **OAuth2 token endpoint (Swagger Authorize):** `POST /auth/token`
- **Header format after login:**

```http
Authorization: Bearer <token>
```

- **Authentication required:**
  - `POST /habits/categories`
  - `PUT /habits/categories/{category_id}`
  - `DELETE /habits/categories/{category_id}`
  - `POST /habits/records`
  - `PUT /habits/records/{record_id}`
  - `DELETE /habits/records/{record_id}`
  - `GET /auth/me`

- **No authentication required:**
  - `GET /`
  - Read endpoints under `/habits` (`GET` list/detail)
  - `GET /analytics/summary`
  - `POST /auth/login`
  - `POST /auth/token`

## 4. Error Handling

Common response status codes:

- **200 OK** – Request succeeded.
- **201 Created** – Resource created successfully.
- **204 No Content** – Resource deleted successfully.
- **400 Bad Request** – Invalid business input (for example duplicate category, invalid category reference).
- **401 Unauthorized** – Missing or invalid authentication credentials.
- **404 Not Found** – Requested resource does not exist.
- **500 Internal Server Error** – Unexpected server-side failure.

Standard error response shape:

```json
{
  "detail": "...",
  "code": "..."
}
```

Notes:
- Validation errors return **422 Unprocessable Entity** and are normalized by the global validation exception handler to the same `detail` + `code` structure.
- Some domain errors expose specific codes (for example: `CATEGORY_NOT_FOUND`, `RECORD_NOT_FOUND`, `CATEGORY_CONFLICT`, `INVALID_CATEGORY`, `AUTH_INVALID_CREDENTIALS`).
- Input constraint highlights implemented in schema validation: category/habit names must be non-empty and max length 100, `category_id` must be `> 0`, and `duration_minutes` must be `>= 0` when provided.

## 5. Endpoint Documentation

---

### 5.0 Service Health

#### GET /

**Purpose**  
Return service status message and API version.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
GET /
```

**Example Response**

```json
{
  "message": "Habit and Productivity Analytics API is running",
  "version": "0.1.0"
}
```

**Status Codes**

- **200 OK** – Service is reachable.

---

### 5.1 Authentication

#### POST /auth/login

**Purpose**  
Authenticate a user and issue a bearer token for protected operations.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body**
  - `username` (string, required)
  - `password` (string, required)
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
POST /auth/login
Content-Type: application/json

{
  "username": "demo",
  "password": "demo123"
}
```

**Example Response**

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

**Status Codes**

- **200 OK** – Login successful.
- **401 Unauthorized** – Incorrect username or password.
- **422 Unprocessable Entity** – Invalid request payload format.

---

#### POST /auth/token

**Purpose**  
OAuth2 password-flow token endpoint used by Swagger UI `Authorize`.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body** (form data)
  - `username` (string, required)
  - `password` (string, required)
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=demo&password=demo123
```

**Example Response**

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

**Status Codes**

- **200 OK** – Token issued.
- **401 Unauthorized** – Incorrect username or password.
- **422 Unprocessable Entity** – Invalid form payload.

---

#### GET /auth/me

**Purpose**  
Return the username bound to the current bearer token.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
GET /auth/me
Authorization: Bearer <token>
```

**Example Response**

```json
{
  "username": "demo"
}
```

**Status Codes**

- **200 OK** – User context returned.
- **401 Unauthorized** – Missing or invalid token.

---

### 5.2 Habit Categories

#### GET /habits/categories

**Purpose**  
List habit categories with pagination controls.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:**
  - `skip` (integer, optional, default: 0)
  - `limit` (integer, optional, default: 50)

**Example Request**

```http
GET /habits/categories?skip=0&limit=50
```

**Example Response**

```json
[
  {
    "id": 1,
    "name": "Fitness",
    "description": "Exercise-related habits"
  },
  {
    "id": 2,
    "name": "Wellness",
    "description": "Sleep and recovery habits"
  }
]
```

**Status Codes**

- **200 OK** – Categories returned.
- **422 Unprocessable Entity** – Invalid query parameter type.

---

#### GET /habits/categories/{category_id}

**Purpose**  
Get a single category by ID.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:**
  - `category_id` (integer, required)
- **Query Parameters:** None

**Example Request**

```http
GET /habits/categories/1
```

**Example Response**

```json
{
  "id": 1,
  "name": "Fitness",
  "description": "Exercise-related habits"
}
```

**Status Codes**

- **200 OK** – Category found.
- **404 Not Found** – Category does not exist.
- **422 Unprocessable Entity** – Invalid path parameter type.

---

#### POST /habits/categories

**Purpose**  
Create a new habit category.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body**
  - `name` (string, required, length: `1..100`)
  - `description` (string, optional)
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
POST /habits/categories
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Fitness",
  "description": "Exercise-related habits"
}
```

**Example Response**

```json
{
  "id": 3,
  "name": "Fitness",
  "description": "Exercise-related habits"
}
```

**Status Codes**

- **201 Created** – Category created.
- **400 Bad Request** – Duplicate category name (business conflict).
- **401 Unauthorized** – Missing or invalid token.
- **422 Unprocessable Entity** – Invalid request payload format.

---

#### PUT /habits/categories/{category_id}

**Purpose**  
Update an existing category by ID.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body**
  - `name` (string, optional, length: `1..100`)
  - `description` (string, optional)
- **Path Parameters:**
  - `category_id` (integer, required)
- **Query Parameters:** None

**Example Request**

```http
PUT /habits/categories/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Fitness",
  "description": "Exercise and movement habits"
}
```

**Example Response**

```json
{
  "id": 1,
  "name": "Fitness",
  "description": "Exercise and movement habits"
}
```

**Status Codes**

- **200 OK** – Category updated.
- **400 Bad Request** – Invalid update data (for example duplicate name).
- **401 Unauthorized** – Missing or invalid token.
- **404 Not Found** – Category does not exist.
- **422 Unprocessable Entity** – Invalid path or payload format.

---

#### DELETE /habits/categories/{category_id}

**Purpose**  
Delete a category by ID.

**Important behavior**  
If records are still linked to the category, delete those records first before deleting the category.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:**
  - `category_id` (integer, required)
- **Query Parameters:** None

**Example Request**

```http
DELETE /habits/categories/1
Authorization: Bearer <token>
```

**Example Response**

```text
(No response body)
```

**Status Codes**

- **204 No Content** – Category deleted.
- **401 Unauthorized** – Missing or invalid token.
- **404 Not Found** – Category does not exist.
- **422 Unprocessable Entity** – Invalid path parameter type.

---

### 5.3 Habit Records

#### GET /habits/records

**Purpose**  
List habit records with pagination controls.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:**
  - `skip` (integer, optional, default: 0)
  - `limit` (integer, optional, default: 100)

**Example Request**

```http
GET /habits/records?skip=0&limit=100
```

**Example Response**

```json
[
  {
    "id": 1,
    "record_date": "2024-06-01",
    "habit_name": "Workout",
    "category_id": 1,
    "completed": true,
    "duration_minutes": 30,
    "notes": "Imported or manually created record"
  }
]
```

**Status Codes**

- **200 OK** – Records returned.
- **422 Unprocessable Entity** – Invalid query parameter type.

---

#### GET /habits/records/{record_id}

**Purpose**  
Get a single habit record by ID.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:**
  - `record_id` (integer, required)
- **Query Parameters:** None

**Example Request**

```http
GET /habits/records/1
```

**Example Response**

```json
{
  "id": 1,
  "record_date": "2024-06-01",
  "habit_name": "Workout",
  "category_id": 1,
  "completed": true,
  "duration_minutes": 30,
  "notes": "Imported or manually created record"
}
```

**Status Codes**

- **200 OK** – Record found.
- **404 Not Found** – Record does not exist.
- **422 Unprocessable Entity** – Invalid path parameter type.

---

#### POST /habits/records

**Purpose**  
Create a new habit record linked to a category.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body**
  - `record_date` (date, required, `YYYY-MM-DD`)
  - `habit_name` (string, required, length: `1..100`)
  - `category_id` (integer, required, must be `> 0`)
  - `completed` (boolean, required)
  - `duration_minutes` (integer, optional, must be `>= 0` when provided)
  - `notes` (string, optional)
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
POST /habits/records
Authorization: Bearer <token>
Content-Type: application/json

{
  "record_date": "2024-06-01",
  "habit_name": "Workout",
  "category_id": 1,
  "completed": true,
  "duration_minutes": 30,
  "notes": "Imported or manually created record"
}
```

**Example Response**

```json
{
  "id": 10,
  "record_date": "2024-06-01",
  "habit_name": "Workout",
  "category_id": 1,
  "completed": true,
  "duration_minutes": 30,
  "notes": "Imported or manually created record"
}
```

**Status Codes**

- **201 Created** – Record created.
- **400 Bad Request** – Invalid referenced category.
- **401 Unauthorized** – Missing or invalid token.
- **422 Unprocessable Entity** – Invalid payload format or field constraints.

---

#### PUT /habits/records/{record_id}

**Purpose**  
Update an existing habit record by ID.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body** (all fields optional)
  - `record_date` (date)
  - `habit_name` (string, length: `1..100`)
  - `category_id` (integer, must be `> 0`)
  - `completed` (boolean)
  - `duration_minutes` (integer, `>= 0`)
  - `notes` (string)
- **Path Parameters:**
  - `record_id` (integer, required)
- **Query Parameters:** None

**Example Request**

```http
PUT /habits/records/10
Authorization: Bearer <token>
Content-Type: application/json

{
  "record_date": "2024-06-02",
  "habit_name": "Workout",
  "category_id": 1,
  "completed": true,
  "duration_minutes": 35,
  "notes": "Updated duration"
}
```

**Example Response**

```json
{
  "id": 10,
  "record_date": "2024-06-02",
  "habit_name": "Workout",
  "category_id": 1,
  "completed": true,
  "duration_minutes": 35,
  "notes": "Updated duration"
}
```

**Status Codes**

- **200 OK** – Record updated.
- **400 Bad Request** – Invalid referenced category.
- **401 Unauthorized** – Missing or invalid token.
- **404 Not Found** – Record does not exist.
- **422 Unprocessable Entity** – Invalid path or payload format.

---

#### DELETE /habits/records/{record_id}

**Purpose**  
Delete a habit record by ID.

**Authentication**  
Required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:**
  - `record_id` (integer, required)
- **Query Parameters:** None

**Example Request**

```http
DELETE /habits/records/10
Authorization: Bearer <token>
```

**Example Response**

```text
(No response body)
```

**Status Codes**

- **204 No Content** – Record deleted.
- **401 Unauthorized** – Missing or invalid token.
- **404 Not Found** – Record does not exist.
- **422 Unprocessable Entity** – Invalid path parameter type.

---

### 5.4 Analytics

#### GET /analytics/summary

**Purpose**  
Return aggregated analytics metrics computed from persisted habit records.

**Authentication**  
Not required.

**Request Body / Path Parameters / Query Parameters**

- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:** None

**Example Request**

```http
GET /analytics/summary
```

**Example Response**

```json
{
  "total_records": 120,
  "completed_records": 86,
  "completion_rate": 71.67,
  "average_duration": 28.5,
  "records_per_category": [
    {
      "category_id": 1,
      "category_name": "Fitness",
      "count": 52
    },
    {
      "category_id": 2,
      "category_name": "Wellness",
      "count": 68
    }
  ],
  "daily_trend": [
    {
      "record_date": "2024-06-01",
      "total": 4,
      "completed": 3
    },
    {
      "record_date": "2024-06-02",
      "total": 5,
      "completed": 4
    }
  ]
}
```

**Status Codes**

- **200 OK** – Summary returned.

## 6. Notes / Usage Remarks

- This API is primarily developed for coursework demonstration and assessment.
- JWT authentication and analytics aggregation are implemented, but the current system remains demo-scale rather than production-scale.
- A pre-deploy seed-once mechanism is implemented via `seed_history` tracking to avoid duplicate imports on redeploy.
- During development, Swagger UI (`/docs`) and ReDoc (`/redoc`) can be used for interactive endpoint inspection.
- The frontend dashboard demonstration flow uses these key API operations: login, create category, create record, delete record, delete category, and refresh analytics summary.
- This document is intended to accompany the GitHub repository and support coursework submission and oral demonstration.

