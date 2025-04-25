import validators
from fastapi import FastAPI, HTTPException

from . import schemas
app = FastAPI()


@app.get("/")
def read_root():
    return "Welcome to URLchemy!"

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

@app.post("/url")
def create_url(url: schemas.URLBase):
    if not validators.url(url.target_url):
        raise_bad_request("Invalid URL")
    # TODO: Here we need to save the URL to our database
    return f"Create data base entry for: {url.target_url}"

