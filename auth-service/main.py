from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import boto3
import jwt
import bcrypt
from datetime import datetime, timedelta
import uuid
from typing import Optional
from dotenv import load_dotenv
import os

app = FastAPI(title="Auth Mikroservis")

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = "eu-north-1"
DYNAMODB_TABLE = "users"
SECRET_KEY = "tajna123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

print(AWS_ACCESS_KEY_ID)


session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE)


class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_jwt_token(email: str, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": email, "id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/register")
# POST /register
# {
#   "email": "email@gmail.com",
#   "password": "sifra123"
# }

async def register(user: UserRegister):
    result = table.get_item(Key={"email": user.email})
    if "Item" in result:
        raise HTTPException(status_code=400, detail="Email već postoji")

    hashed_pw = hash_password(user.password)
    user_id = str(uuid.uuid4())

    table.put_item(Item={
        "id": user_id,
        "email": user.email,
        "password": hashed_pw
    })

    return {"message": "Registracija uspjesna"}


@app.post("/login")

# POST /login
# {
#   "email": "email@gmail.com",
#   "password": "sifra123"
# }
# ===OUTPUT===
# {
#     "access_token": "eyJ....",    
#     "token_type": "bearer"
# }

async def login(user: UserLogin):
    result = table.get_item(Key={"email": user.email})
    if "Item" not in result:
        raise HTTPException(status_code=401, detail="Neispravni podaci")

    item = result["Item"]
    if not verify_password(user.password, item["password"]):
        raise HTTPException(status_code=401, detail="Neispravni podaci")

    token = create_jwt_token(email=item["email"], user_id=item["id"])
    return {"access_token": token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
