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

# check db for active db entries provided w/ non secret key
def get_db_url_by_key(db: Session, url_key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )

# check db for active db entries provided w/ secret key
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
def deactivate_db_url_by_secret_key(
    db: Session, secret_key: str
) -> models.URL:
    db_url = get_db_url_by_secret_key(db, secret_key)
    if db_url:
        db_url.is_active = False
        db.commit()
        db.refresh(db_url)
    return db_url

# query unique urls for db viz
def get_unique_urls(db: Session):
    return db.query(URL.target_url).distinct().filter(URL.is_active == True).all()