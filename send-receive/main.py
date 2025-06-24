from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Send/Receive Mikroservis")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = "eu-north-1"
DYNAMODB_TABLE = "packages"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)



class PackageSend(BaseModel):
    sender_name: str
    delivery_location: str

class LocationUpdate(BaseModel):
    location: str



@app.post("/send-package")
async def send_package(data: PackageSend):
    package_id = str(uuid.uuid4())
    send_time = datetime.utcnow().isoformat()

    item = {
        "package_id": package_id,
        "sender_name": data.sender_name,
        "delivery_location": data.delivery_location,
        "sent_at": send_time,
        "is_delivered": False,
        "delivered_at": None,
        "current_location_history": [data.delivery_location]  
    }

    table.put_item(Item=item)
    return {"message": "Paket uspješno poslan", "package_id": package_id}



@app.post("/deliver-package/{package_id}")
async def deliver_package(package_id: str):
    result = table.get_item(Key={"package_id": package_id})
    if "Item" not in result:
        raise HTTPException(status_code=404, detail="Paket nije pronađen")

    delivered_time = datetime.utcnow().isoformat()

    table.update_item(
        Key={"package_id": package_id},
        UpdateExpression="SET is_delivered = :del, delivered_at = :dt",
        ExpressionAttributeValues={
            ":del": True,
            ":dt": delivered_time
        }
    )

    return {"message": "Paket označen kao preuzet", "delivered_at": delivered_time}



@app.post("/update-location/{package_id}")
async def update_location(package_id: str, data: LocationUpdate):
    result = table.get_item(Key={"package_id": package_id})
    if "Item" not in result:
        raise HTTPException(status_code=404, detail="Paket nije pronađen")

    table.update_item(
        Key={"package_id": package_id},
        UpdateExpression="SET current_location_history = list_append(current_location_history, :loc)",
        ExpressionAttributeValues={
            ":loc": [data.location]
        }
    )

    return {"message": f"Lokacija '{data.location}' dodana za paket {package_id}"}



@app.get("/get-package/{package_id}")
async def get_package(package_id: str):
    result = table.get_item(Key={"package_id": package_id})
    if "Item" not in result:
        raise HTTPException(status_code=404, detail="Paket nije pronađen")

    return result["Item"]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
