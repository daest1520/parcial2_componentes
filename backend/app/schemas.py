from datetime import date
from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=1, max_length=120)
    startDate: date
    endDate: date


class PlaceCreate(BaseModel):
    tripId: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=1000)
    city: str = Field(min_length=1, max_length=100)
    categoryId: int = Field(gt=0)
    tentativeDate: date
