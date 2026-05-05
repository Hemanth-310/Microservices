from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import csv
import io
from pymongo import MongoClient
import os

app = FastAPI()
security = HTTPBearer()

# IMPORTANT: Use the SAME secret key as auth service
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client.inventory_db
collection = db.items

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user email"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    email: str = Depends(verify_token)
):
    # Check if it's CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files allowed")
    
    # Read file content
    content = await file.read()
    
    # Parse CSV
    csv_data = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    # Insert into MongoDB
    items_inserted = 0
    
    for row in csv_reader:
        try:
            # Extract only needed columns
            item = {
                "region": row.get("Region", ""),
                "product": row.get("Product", ""),
                "location": row.get("Location", ""),
                "order_qty": int(row.get("order_qty", 0)),
                "curr_inv": int(row.get("curr_inv", 0)),
                "supp_qty": int(row.get("supp_qty", 0)),
                "on_hand_qty": int(row.get("on_hand_qty", 0)),
                "uploaded_by": email  # Track who uploaded
            }
            
            # Create unique ID from product + location + region
            unique_id = f"{item['product']}_{item['location']}_{item['region']}"
            
            # Insert or update
            collection.update_one(
                {"_id": unique_id},
                {"$set": item},
                upsert=True
            )
            items_inserted += 1
            
        except Exception as e:
            print(f"Error: {e}, Row: {row}")
            continue
    
    return {
        "message": "Upload successful",
        "items_processed": items_inserted,
        "uploaded_by": email
    }

@app.get("/health")
def health():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
