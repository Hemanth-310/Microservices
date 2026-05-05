from fastapi import FastAPI, Query, HTTPException, Depends, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pymongo import MongoClient
from typing import Optional

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

@app.get("/restock")
def get_restock_items(
    threshold: int = Query(10, description="Stock below this threshold needs restock"),
    region: Optional[str] = None,
    product: Optional[str] = None,
    email: str = Depends(verify_token)
):
    """Get items that need restocking (curr_inv < threshold)"""
    
    # Build query
    query = {"curr_inv": {"$lt": threshold}}
    
    # Add filters if provided
    if region:
        query["region"] = region
    if product:
        query["product"] = product
    
    # Get items
    items = list(collection.find(
        query,
        {
            "_id": 0,
            "region": 1,
            "product": 1,
            "location": 1,
            "curr_inv": 1,
            "order_qty": 1,
            "supp_qty": 1,
            "on_hand_qty": 1
        }
    ).sort("curr_inv", 1))
    
    return {
        "items": items,
        "count": len(items),
        "threshold": threshold,
        "requested_by": email
    }

@app.get("/restock/my-items")
def get_my_restock_items(
    threshold: int = Query(10),
    email: str = Depends(verify_token)
):
    """Get restock items ONLY for items uploaded by this user"""
    
    items = list(collection.find(
        {
            "curr_inv": {"$lt": threshold},
            "uploaded_by": email
        },
        {
            "_id": 0,
            "region": 1,
            "product": 1,
            "location": 1,
            "curr_inv": 1,
            "order_qty": 1,
            "supp_qty": 1,
            "on_hand_qty": 1,
            "uploaded_by": 1
        }
    ).sort("curr_inv", 1))
    
    return {
        "items": items,
        "count": len(items),
        "user": email,
        "threshold": threshold
    }

# DELETE endpoints for removing items
@app.delete("/items/{product_id}")
def delete_item_by_product(
    product_id: str,
    location: Optional[str] = None,
    region: Optional[str] = None,
    email: str = Depends(verify_token)
):
    """
    Delete an item by product ID
    Optional filters: location, region
    Only the user who uploaded can delete (unless admin)
    """
    
    # Build query
    query = {"product": product_id}
    
    if location:
        query["location"] = location
    if region:
        query["region"] = region
    
    # Check if item exists
    item = collection.find_one(query)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if user owns this item (or you can skip this for admin)
    if item.get("uploaded_by") != email:
        raise HTTPException(status_code=403, detail="You can only delete items you uploaded")
    
    # Delete the item
    result = collection.delete_one(query)
    
    return {
        "message": f"Item '{product_id}' deleted successfully",
        "deleted_count": result.deleted_count,
        "deleted_by": email
    }

@app.delete("/items")
def delete_items_by_filters(
    region: Optional[str] = None,
    product: Optional[str] = None,
    location: Optional[str] = None,
    email: str = Depends(verify_token)
):
    """
    Delete multiple items by filters
    Can delete by region, product, or location
    """
    
    # Build query
    query = {}
    if region:
        query["region"] = region
    if product:
        query["product"] = product
    if location:
        query["location"] = location
    
    if not query:
        raise HTTPException(status_code=400, detail="At least one filter is required")
    
    # Add user filter (only delete their own items)
    query["uploaded_by"] = email
    
    # Check how many will be deleted
    count = collection.count_documents(query)
    if count == 0:
        raise HTTPException(status_code=404, detail="No matching items found")
    
    # Delete items
    result = collection.delete_many(query)
    
    return {
        "message": f"Deleted {result.deleted_count} items",
        "filters_applied": {
            "region": region,
            "product": product,
            "location": location
        },
        "deleted_by": email
    }

@app.delete("/items/all/my")
def delete_all_my_items(
    email: str = Depends(verify_token)
):
    """Delete ALL items uploaded by the current user"""
    
    # Count items before deletion
    count = collection.count_documents({"uploaded_by": email})
    
    if count == 0:
        raise HTTPException(status_code=404, detail="No items found for this user")
    
    # Delete all user's items
    result = collection.delete_many({"uploaded_by": email})
    
    return {
        "message": f"Deleted all {result.deleted_count} items uploaded by you",
        "user": email
    }

@app.get("/health")
def health():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
