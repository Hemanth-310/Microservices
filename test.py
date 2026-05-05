import requests

# Upload CSV
print("Uploading CSV...")
with open("sample.csv", "rb") as f:
    response = requests.post("http://localhost:8001/upload", files={"file": f})
print(response.json())

print("\n" + "="*50)
print("ITEMS NEEDING RESTOCK (Stock < 10)")
print("="*50)

# Get restock items
response = requests.get("http://localhost:8002/restock")
data = response.json()

print(f"\nFound {data['count']} items that need restock:\n")

for item in data['items']:
    print(f"Product: {item['product']}")
    print(f"  Location: {item['location']} ({item['region']})")
    print(f"  Current Stock: {item['curr_inv']}")
    print(f"  On Hand: {item['on_hand_qty']}")
    print(f"  Order Quantity: {item['order_qty']}")
    print(f"  Supply Quantity: {item['supp_qty']}")
    print("-" * 40)

# Test with region filter
print("\n" + "="*50)
print("NORTH AMERICA ONLY")
print("="*50)
response = requests.get("http://localhost:8002/restock?region=North%20America")
data = response.json()
for item in data['items']:
    print(f"{item['product']} in {item['location']}: {item['curr_inv']} units")