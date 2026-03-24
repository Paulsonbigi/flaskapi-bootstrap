
from sqlalchemy import String, Integer, Column
from app.database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    first_name   = Column(String, nullable=False)
    last_name    = Column(String, nullable=False)
    email        = Column(String, unique=True, nullable=False, index=True)
    password     = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
