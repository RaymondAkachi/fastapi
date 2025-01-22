from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Union
# from pydantic.types import conint
from typing_extensions import Annotated
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True


class PostCreate(PostBase):  # Pydantic mode that accepts entries for users
    pass

# This class is is running but is currenltly not behaving how it's supposed to troubleshoot as 5:45:52


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Output(PostBase):
    id: int  # Pydantic model that send message to users
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:  # This class and it's variable are needed by fastapi for output
        orm_mode = True


class PostOut(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    votes: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    # id: Optional[str] = None
    id: Union[str, int]


class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(strict=True, le=1)]

# class Foo(BaseModel):
#             bar: Annotated[int, Field(strict=True, lt=1)]
# Changed at 9:38:12
