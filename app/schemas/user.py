from typing import List
from pydantic import BaseModel


class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    profile_image: str
    phone_number: str