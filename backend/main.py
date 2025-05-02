import validators
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.datastructures import URL

from . import crud, models, schemas
from .database import SessionLocal, engine
from .config import get_settings
from .scraper import scrape_metadata

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


# dependency to get database session going and close in case of errors
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# public info -> shortened URL
def get_public_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    return schemas.URLInfo(
        url=str(base_url.replace(path=db_url.key)),
        target_url=db_url.target_url,
        title=db_url.title,
        description=db_url.description,
        is_active=db_url.is_active,
        clicks=db_url.clicks,
    )


# admin info (public info + secret keys) -> shortened URL
def get_admin_info(db_url: models.URL) -> schemas.URLAdminInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for(
        "administration info", secret_key=db_url.secret_key
    )
    return schemas.URLAdminInfo(
        **get_public_info(db_url).model_dump(),  # using model_dump from pydantic
        admin_url=str(base_url.replace(path=admin_endpoint)),
    )


@app.get("/")
def read_root():
    return "Welcome to URLchemy!"


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    message = f"Page '{request.url}' Not Found"
    raise HTTPException(status_code=404, detail=message)


@app.post("/url")
def create_url(url: schemas.URLBase, db: Session = Depends(get_db)):
    """
    Create a shortened URL and scrape metadata for the given target URL.

    :param url (schemas.URLBase): The target URL to be shortened.
    :param db (Session): The database session.
    :return: (dict) A dictionary containing the shortened URL and its metadata.
    :raises HTTPException: If the provided URL is invalid.
    """
    metadata = scrape_metadata(url.target_url)
    db_url = crud.create_db_url(
        db=db,
        url=url,
        title=metadata.get("title", "No title found"),
        description=metadata.get("description", "No description found"),
    )

    return {
        "shortened_url": get_public_info(db_url)
    }




# call for requested url to point to host and key pattern
@app.get("/{url_key}")
def forward_to_target_url(
        url_key: str, request: Request, db: Session = Depends(get_db)
):
    """
    Redirect to the target URL associated with the given shortened URL key.

    :param url_key (str): The key of the shortened URL.
    :param request (Request): The incoming HTTP request.
    :param db (Session): The database session.
    :return: (RedirectResponse) Redirects to the target URL.
    :raises HTTPException: If the URL key is not found or inactive.
    """
    # walrus operator for matching url found
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_db_clicks(db=db, db_url=db_url)  # increment click count
        # redirect to target url
        return RedirectResponse(db_url.target_url)
    else:
        # raise 404 error if key is not found or inactive
        raise_not_found(request)


# call for requested url to point to host and secret key pattern
@app.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=schemas.URLAdminInfo,
)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    """
    Retrieve administrative information for a shortened URL using the secret key.

    :param secret_key (str): The secret key of the shortened URL.
    :param request (Request): The incoming HTTP request.
    :param db (Session): The database session.
    :return: (schemas.URLAdminInfo) Administrative information about the shortened URL.
    :raises HTTPException: If the secret key is not found or inactive.
    """
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


# endpoint to deactivate shortened url using secret key
@app.delete("/admin/{secret_key}")
def delete_url(secret_key: str, request: Request, db: Session = Depends(get_db)):
    """
    Deactivate a shortened URL using the secret key.

    :param secret_key (str): The secret key of the shortened URL.
    :param request (Request): The incoming HTTP request.
    :param db (Session): The database session.
    :return: (dict) A message confirming the deletion of the shortened URL.
    :raises HTTPException: If the secret key is not found or already deactivated.
    """
    if db_url := crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)  # raise 404 error if key is not found or deactivated


@app.get("/data/urls")
def get_urls_table(db: Session = Depends(get_db)):
    """
    Retrieve a table of unique URLs from the database, grouped by domain.

    This endpoint checks if the 'urls' table exists in the database. If it does,
    it retrieves all rows from the table, extracts unique domains, and returns
    the first entry for each domain.

    :param db (Session): The database session.
    :return: (JSONResponse) A JSON response containing the unique URLs grouped by domain.
    :raises HTTPException: If the 'urls' table is not found or an error occurs during execution.
    """
    try:
        table_exists = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='urls';")
        ).fetchone()
        if not table_exists:
            raise HTTPException(status_code=404, detail="Table 'urls' not found")

        rows = db.execute(text("SELECT * FROM urls")).fetchall()
        columns = [col[1] for col in db.execute(text("PRAGMA table_info('urls')"))]
        data = [dict(zip(columns, row)) for row in rows]

        unique_domains = {}
        for entry in data:
            domain = urlparse(entry["target_url"]).netloc
            if domain not in unique_domains:
                unique_domains[domain] = entry

        return JSONResponse(content={"data": list(unique_domains.values())})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")