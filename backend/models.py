from sqlalchemy import Boolean, Column, Integer, String

from .database import Base

# db model for our urls
class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)              # primary key
    key = Column(String, unique=True, index=True)       # randomly generated key
    secret_key = Column(String, unique=True, index=True)# url management and stats for our scraper?
    target_url = Column(String, index=True)             # where the provided shortened url points to
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)                 # number of clicks on url
