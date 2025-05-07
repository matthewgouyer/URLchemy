# Code adapted from Real Python Tutorial: https://realpython.com/build-a-python-url-shortener-with-fastapi/
# Modifications: Title and Description added to schema, config class, separate schema for admin url
from sqlalchemy import Boolean, Column, Integer, String
from pydantic import BaseModel

# shortened url gets stored
class URLBase(BaseModel):
    target_url: str

# public info from shortened url
class URLInfo(BaseModel):
    url: str
    target_url: str
    title: str = "No title found"               # metadata scraped
    description: str = "No description found"   # metadata scraped
    is_active: bool
    clicks: int

    # give config to pydantic to allow for attributes to be used
    class Config:
        from_attributes = True

# admin url info seperated from public
class URLAdminInfo(URLInfo):
    admin_url: str