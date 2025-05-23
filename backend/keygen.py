# Code adapted from Real Python Tutorial: https://realpython.com/build-a-python-url-shortener-with-fastapi/
import secrets
import string

from sqlalchemy.orm import Session

from . import crud

# generate a random key of given length instead of hard code in main.py
def create_random_key(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_random_key(db: Session) -> str:
    key = create_random_key()
    # check if key already exists in db
    while crud.get_db_url_by_key(db, key):
        key = create_random_key()
    return key
