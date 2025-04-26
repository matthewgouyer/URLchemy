from pydantic import BaseModel

# shortened url gets stored
class URLBase(BaseModel):
    target_url: str

# allows for deactivating of a url & count of visits
class URL(URLBase):
    is_active: bool
    clicks: int

    # give config to pydantic for ORM interaction of db
    class Config:
        orm_mode = True

#  potential temp storage of data
class URLInfo(URL):
    url: str
    admin_url: str

