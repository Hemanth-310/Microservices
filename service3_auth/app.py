from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import hashlib
import secrets

app = FastAPI()
security = HTTPBearer()

# Security configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client.inventory_db
users_collection = db.users

# Create index for faster lookups
users_collection.create_index("email", unique=True)

# Pydantic Models
class UserSignup(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Simple password hashing using SHA256 (works perfectly, no bcrypt issues)
def get_password_hash(password: str) -> str:
    """Hash password using SHA256 with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    salt, stored_hash = hashed_password.split(":")
    hash_obj = hashlib.sha256((plain_password + salt).encode())
    return hash_obj.hexdigest() == stored_hash

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    """Verify JWT token and return email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(401, "Invalid token")
        return email
    except JWTError:
        raise HTTPException(401, "Invalid token")

# API Endpoints
@app.post("/signup")
def signup(user: UserSignup):
    # Check if user exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    users_collection.insert_one({
        "email": user.email,
        "password": hashed_password,
        "name": user.name,
        "created_at": datetime.utcnow()
    })
    
    return {
        "message": "User created successfully",
        "email": user.email,
        "name": user.name
    }

@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    # Find user
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/verify")
def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if token is valid"""
    email = verify_token(credentials.credentials)
    return {"email": email, "valid": True, "message": "Token is valid"}

@app.delete("/user/{email}")
def delete_user(email: str):
    """Delete user (for testing purposes)"""
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(404, "User not found")
    return {"message": f"User {email} deleted successfully"}

@app.get("/health")
def health():
    return {"status": "alive", "service": "auth", "version": "simple"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
