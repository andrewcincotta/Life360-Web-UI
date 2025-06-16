from pydantic import BaseModel


class Circle(BaseModel):
    id: str
    name: str


class Member(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
