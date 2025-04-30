from pydantic import BaseModel

# shortened url gets stored
class URLBase(BaseModel):
    target_url: str

# public info from shortened url
class URLInfo(BaseModel):
    url: str
    target_url: str
    is_active: bool
    clicks: int

    # give config to pydantic to allow for attributes to be used
    class Config:
        from_attributes = True

# admin url info seperated from public
class URLAdminInfo(URLInfo):
    admin_url: str