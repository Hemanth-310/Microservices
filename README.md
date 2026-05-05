
# 🚀 Microservices Inventory Management System

A microservices architecture for inventory management with file upload, inventory tracking, and authentication services built with FastAPI and MongoDB.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![Microservices](https://img.shields.io/badge/Architecture-Microservices-red.svg)](https://microservices.io/)
[![JWT](https://img.shields.io/badge/Auth-JWT-orange.svg)](https://jwt.io/)

* * *

## 📜 Introduction and Problem Statement

Traditional monolithic inventory systems face challenges with **scalability, maintainability, and independent deployments**. Core problems include:

*   🏗️ **Tight Coupling** - Changes in one module affect the entire system
*   📈 **Scaling Limitations** - Cannot scale individual components independently
*   🔧 **Maintenance Complexity** - Large codebase becomes hard to manage
*   🚀 **Slow Deployments** - Even small changes require full system redeployment

This project implements a **microservices-based solution** that decomposes inventory management into three independent services:

*   🔐 **Auth Service** - Handles user authentication and JWT token management
*   📤 **Upload Service** - Processes CSV files and validates inventory data
*   📦 **Inventory Service** - Manages CRUD operations for inventory items

All services communicate via HTTP and can be deployed, scaled, and maintained independently.

* * *

## 🎯 Key Objectives

The project has four main objectives:

1.  **Implement Service Isolation** - Create loosely coupled services with single responsibilities
2.  **Enable JWT-Based Security** - Secure all endpoints with token-based authentication
3.  **Provide Batch Data Processing** - Handle CSV file uploads for bulk inventory updates



### Service Communication Flow

1.  Client authenticates via **Auth Service** to receive JWT token
2.  Token is included in all subsequent requests
3.  **Upload Service** validates token, processes CSV, and forwards to Inventory Service
4.  **Inventory Service** validates token and performs database operations

* * *

## 🗄️ MongoDB Database Schema

### Users Collection (`users`)
```json
{
  "_id": ObjectId,
  "username": "string (unique)",
  "password": "string (hashed with bcrypt)",
  "created_at": "datetime"
}
```

### Inventory Collection (`inventory`)
```json
{
  "_id": ObjectId,
  "product_id": "string (unique)",
  "name": "string",
  "category": "string",
  "quantity": "integer",
  "price": "float",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

* * *

## 🚀 Installation

### Prerequisites

*   Python 3.10 or higher
*   pip package manager
*   MongoDB

### Step 1: Clone the Repository

```bash
git clone https://github.com/Hemanth-310/Microservices.git
cd Microservices
```

### Step 2: Start MongoDB

**Local Installation:**
```bash
# Start MongoDB service
brew services start mongodb-community

```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure MongoDB Connection

Edit each service's `app.py` to update MongoDB connection if needed:

```python
# Default connection (local MongoDB)
client = MongoClient("mongodb://localhost:27017")
db = client["inventory_db"]

# For MongoDB Atlas, use:
# client = MongoClient("mongodb+srv://username:password@cluster.mongodb.net/")
```

### Step 5: Run the Services

**Terminal 1 - Auth Service:**
```bash
cd service3_auth
python app.py
# Running on http://localhost:8003
```

**Terminal 2 - Inventory Service:**
```bash
cd service2_inventory
python app.py
# Running on http://localhost:8002
```

**Terminal 3 - Upload Service:**
```bash
cd service1_upload
python app.py
# Running on http://localhost:8001
```

* * *

## 📡 API Endpoints

### 1️⃣ Auth Service (`port 8003`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/login` | Login and get JWT token |
| GET | `/verify` | Verify JWT token |
| GET | `/health` | Health check |

### 2️⃣ Upload Service (`port 8001`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/upload` | Upload CSV file with inventory data | JWT Required |
| GET | `/health` | Health check | None |

### 3️⃣ Inventory Service (`port 8002`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/restock` | Get all items with stock < 10 | JWT Required |
| GET | `/restock/my-items` | View only items uploaded by you | JWT Required |
| DELETE | `/items/{product_name}` | Delete single item by product name | JWT Required |
| DELETE | `/items?region={region}` | Delete all items in a region | JWT Required |
| DELETE | `/items?product={name}` | Delete all items with specific product | JWT Required |
| DELETE | `/items/all/my` | Delete all items uploaded by you | JWT Required |
| GET | `/health` | Health check | None |
* * *

## 📦 Sample CSV Format

The upload service expects CSV files in this format:

```csv
product_id,name,category,quantity,price
INV-001,Laptop,Electronics,50,999.99
INV-002,Mouse,Electronics,200,29.99
INV-003,Desk,Furniture,25,199.99
INV-004,Monitor,Electronics,35,299.99
INV-005,Keyboard,Electronics,150,79.99
```

* * *

## 🧪 Testing with Postman

### Import Postman Collection

1. Download `Inventory_Microservice_Collection.json` from this repository
2. Open Postman
3. Click **Import** button
4. Select the JSON file
5. All endpoints will be pre-configured

### Testing Workflow

**Step 1: Health Checks (Optional)**
- `GET {{base_url_auth}}/health` - Check if Auth Service is running
- `GET {{base_url_upload}}/health` - Check if Upload Service is running  
- `GET {{base_url_inventory}}/health` - Check if Inventory Service is running

**Step 2: Sign Up - Create New User**
- Request: `POST {{base_url_auth}}/signup`
- Body:
```json
{
    "email": "testuser@example.com",
    "password": "testpass123",
    "name": "Test User"
}
```
**Step 3: Login - Get JWT Token**

- Request: POST {{base_url_auth}}/login
- Body:
```json
{
    "email": "testuser@example.com",
    "password": "testpass123"
}
```
Important: The Postman collection automatically saves the returned access_token to the collection variable

**Step 4: Verify Token**

- Request: GET {{base_url_auth}}/verify
- Headers: Authorization: Bearer {{access_token}}

**Step 5: Upload CSV File**

- Request: POST {{base_url_upload}}/upload
- Headers: Authorization: Bearer {{access_token}}
- Body: Select file (form-data) with key "file" and choose sample.csv

**Step 6: View Inventory Operations**

- Endpoint	Description
- GET {{base_url_inventory}}/restock	Get all items with stock < 10
- GET {{base_url_inventory}}/restock?region=Europe	Filter items by region (Europe, North America, Asia, etc.)
- GET {{base_url_inventory}}/restock?threshold=20	Custom stock threshold (stock < 20)
- GET {{base_url_inventory}}/restock?product=Mouse	Filter by product name
- GET {{base_url_inventory}}/restock?region=Europe&threshold=15	Multiple filters (region + threshold)
- GET {{base_url_inventory}}/restock/my-items	View only items uploaded by you
- GET {{base_url_inventory}}/restock/my-items?threshold=20	Your items with custom threshold

**Step 7: Delete Operations (With Authentication)**

- Endpoint	Description
- DELETE {{base_url_inventory}}/items/Webcam	Delete single item by product name
- DELETE {{base_url_inventory}}/items/Wireless%20Mouse?location=Chicago&region=North%20America	Delete with location and region filters
- DELETE {{base_url_inventory}}/items?region=Europe	Delete all items in a region
- DELETE {{base_url_inventory}}/items?product=Wireless%20Mouse	Delete all items with specific product name
- DELETE {{base_url_inventory}}/items/all/my	Delete all items uploaded by you
- Sample CSV Format
* * *

## 📁 Project Structure

```
Microservices/
├── service1_upload/           
│   ├── app.py                 
│   └── requirements.txt       
├── service2_inventory/        
│   ├── app.py                 
│   └── requirements.txt       
├── service3_auth/             
│   ├── app.py                 
│   └── requirements.txt       
├── Inventory_Microservice_Collection.json  
├── requirements.txt           
├── sample.csv                 
└── README.md                  
```

* * *

## 📦 Dependencies

Key dependencies include:

*   **fastapi** - Modern web framework for building APIs
*   **uvicorn** - ASGI server for running FastAPI
*   **pymongo** - MongoDB driver for Python
*   **python-jose** - JWT encoding and decoding
*   **passlib** + **bcrypt** - Password hashing
*   **pandas** - CSV file processing
*   **python-multipart** - File upload handling
*   **httpx** - Async HTTP client for service communication


* * *

## 🔧 Configuration

### MongoDB Connection
In each service's `app.py`:

```python
# Local MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["inventory_db"]

# MongoDB Atlas (cloud)
client = MongoClient("mongodb+srv://username:password@cluster.mongodb.net/")
```

### JWT Secret
In `service3_auth/app.py`:

```python
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 Minutes
```

* * *

## 💬 Discussion and Results

### Achievements

*   ✅ **Successful Service Isolation** - Three independent services with clear boundaries
*   ✅ **JWT Authentication** - Secure token-based authentication
*   ✅ **CSV Batch Processing** - Bulk upload capability with pandas integration
*   ✅ **Interactive Documentation** - Auto-generated Swagger UI for each service
*   ✅ **MongoDB Integration** - Persistent storage with flexible schema


### Security Features

*   🔐 **bcrypt Password Hashing** - Secure password storage
*   🎫 **JWT Tokens** - Stateless authentication with expiration
*   🛡️ **Service Isolation** - Each service runs independently
*   ✅ **Input Validation** - All endpoints validate request data


* * *


## 🐛 Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Restart MongoDB
brew services restart mongodb-community
```

### Port Already in Use
```bash
# Find process using port (e.g., 8001)
lsof -i :8001
kill -9 <PID>
```

### Authentication Failed
- Ensure JWT token is included in Authorization header
- Format: `Bearer your-jwt-token-here`
- Token expires after specific hours - login again

### CSV Upload Fails
- Verify CSV format matches `sample.csv`
- Check file size (< 10MB)
- Ensure authentication token is valid

* * *

## 👥 Author

**Hemanth**
