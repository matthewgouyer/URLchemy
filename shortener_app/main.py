import validators
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# dependency to get database session going and close incase of errors
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return "Welcome to URLchemy!"

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

def raise_not_found(request):
    message = f"Page '{request.url}' Not Found"
    raise HTTPException(status_code=404, detail=message)

@app.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")

    db_url = crud.create_db_url(db=db, url=url)
    db_url.url = db_url.key
    db_url.admin_url = db_url.secret_key

    return db_url

# call for requested url to point to host and key pattern
@app.get("/{url_key}")
def forward_to_target_url(
    url_key: str, request: Request, db: Session = Depends(get_db)
):
    # query DB for URL w/ given key
    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )
    # walrus operator for matching url found
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        # redirect to target url
        return RedirectResponse(db_url.target_url)
    else:
        # raise 404 error if key is not found or inactive
        raise_not_found(request)