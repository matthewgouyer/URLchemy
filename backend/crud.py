# Code adapted from Real Python Tutorial: https://realpython.com/build-a-python-url-shortener-with-fastapi/
# Modifications: Url creation
from sqlalchemy.orm import Session

from . import keygen, models, schemas
from backend.keygen import create_random_key
from .models import URL

# create a new db entry for shortened url
def create_db_url(db: Session, url: schemas.URLBase, title: str, description: str) -> models.URL:
    db_url = models.URL(
        target_url=url.target_url,
        key=create_random_key(),
        secret_key=create_random_key(),
        title=title,
        description=description
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

# check db for active db entries provided w/ key type
def get_url_by_key_type(db: Session, key: str, key_type: str) -> models.URL:
    filter_condition = models.URL.key if key_type == "key" else models.URL.secret_key
    return (
        # query db for key type
        db.query(models.URL).filter(filter_condition == key, models.URL.is_active).first()
    )

# tried to consolidate the two functions above but it didn't work correctly and is messy
def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.secret_key == secret_key, models.URL.is_active)
        .first()
    )

# db click count for shortened url
def update_db_clicks(db: Session, db_url: models.URL) -> models.URL:
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url

# user deactivation w/ admin final say
def deactivate_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL:
    db_url = get_url_by_key_type(db, secret_key, key_type="secret_key")
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url
