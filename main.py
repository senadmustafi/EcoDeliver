from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Radi!"}


@app.post("/post")
def post_root(data: dict):
    print(data)
    return {"message": "Radi!"}
