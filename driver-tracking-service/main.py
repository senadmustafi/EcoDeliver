from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Driver Mikroservis")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = "eu-north-1"
DYNAMODB_TABLE = "drivers"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)



class DriverInfo(BaseModel):
    driver_id: str
    full_name: str
    vehicle: str
    category: str  
    registration_plate: str

class LocationUpdate(BaseModel):
    location: str

class StatusUpdate(BaseModel):
    status: str  



@app.post("/driver")
async def upsert_driver(data: DriverInfo):
    table.put_item(
        Item={
            "driver_id": data.driver_id,
            "full_name": data.full_name,
            "vehicle": data.vehicle,
            "category": data.category,
            "registration_plate": data.registration_plate,
            "status": "offline",
        }
    )
    return {"message": "Podaci o vozaču spremljeni"}



@app.get("/driver/{driver_id}")
async def get_driver(driver_id: str):
    result = table.get_item(Key={"driver_id": driver_id})
    if "Item" not in result:
        raise HTTPException(status_code=404, detail="Vozač nije pronađen")
    return result["Item"]





@app.post("/driver/{driver_id}/status")
async def update_status(driver_id: str, data: StatusUpdate):
    result = table.get_item(Key={"driver_id": driver_id})
    if "Item" not in result:
        raise HTTPException(status_code=404, detail="Vozač nije pronađen")

    table.update_item(
        Key={"driver_id": driver_id},
        UpdateExpression="SET #st = :s",
        ExpressionAttributeNames={"#st": "status"},
        ExpressionAttributeValues={":s": data.status},
    )
    return {"message": "Status ažuriran"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
