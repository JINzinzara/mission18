from typing import Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, HttpUrl


class MovieCreate(BaseModel):
    model_config = {"str_strip_whitespace": True}  # 빈 문자열 + 공백 입력 거부
    title: str = Field(min_length=1)
    release_date: date
    director: str = Field(min_length=1)
    genre: str = Field(min_length=1)
    poster_url: HttpUrl


class MovieOut(MovieCreate):
    id: int = Field(gt=0)


class MovieScoreOut(BaseModel):
    movie_id: int = Field(gt=0)
    count: int = Field(ge=0)
    average: float | None = Field(ge=0, le=1)


class ReviewCreate(BaseModel):
    model_config = {"str_strip_whitespace": True}
    movie_id: int = Field(gt=0)
    author: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ReviewOut(ReviewCreate):
    model_config = {"from_attributes": True}
    id: int = Field(gt=0)
    created_at: datetime
    sentiment: Literal["긍정", "부정"]
    sentiment_score: float = Field(ge=0, le=1)
