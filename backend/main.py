from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from database import execute, create_tables, fetch_all, fetch_one
from sentiment import load_model, analyze
from schemas import MovieCreate, MovieOut, MovieScoreOut, ReviewCreate, ReviewOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 실행 시 모델 로드 및 create_tables 준비"""
    create_tables()
    load_model()
    yield


app = FastAPI(title="영화 리뷰 API", lifespan=lifespan)


# Movie functions
@app.get(
    "/movies",
    response_model=list[MovieOut],
    tags=["영화"],
    summary="영화 목록 조회",
    description="등록된 영화 전체를 ID의 오름차순으로 조회. 영화가 없을 시 빈 목록 반환",
)
def list_movies():
    """영화의 전체 목록 반환"""
    # ORDER BY id ASC: id의 오름차순으로 정리
    return fetch_all("SELECT * FROM movies ORDER BY id ASC")


@app.post(
    "/movies",
    response_model=MovieOut,
    status_code=201,
    tags=["영화"],
    summary="영화 등록",
    description="입력한 영화 정보를 DB에 저장하고, 생성된 ID를 포함한 영화 정보를 반환",
)
def create_movie(movie: MovieCreate):
    """영화 생성/추가"""
    new_id = execute(
        "INSERT INTO movies (title, release_date, director, genre, poster_url) VALUES (?, ?, ?, ?, ?)",
        (
            movie.title,
            movie.release_date.isoformat(),
            movie.director,
            movie.genre,
            str(movie.poster_url),
        ),
    )
    return fetch_one("SELECT * FROM movies WHERE id = ?", (new_id,))


@app.get(
    "/movies/{movie_id}",
    response_model=MovieOut,
    tags=["영화"],
    summary="특정 영화 조회",
    description="영화 ID에 해당하는 정보 반환. 해당 영화가 없을 시 404 반환",
)
def get_movie(movie_id: int):
    """특정 영화 조회"""
    movie = fetch_one("SELECT * FROM movies WHERE id = ?", (movie_id,))
    if movie is None:
        raise HTTPException(404, f"{movie_id}번에 해당하는 영화가 없습니다")
    return movie


@app.delete(
    "/movies/{movie_id}",
    response_model=MovieOut,
    tags=["영화"],
    summary="영화 삭제",
    description="영화와 해당하는 영화의 리뷰를 삭제하고 삭제된 영화 정보 반환. 영화가 없을 시 404 반환",
)
def delete_movie(movie_id: int):
    """영화 삭제"""
    movie = get_movie(movie_id)
    execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    return movie


# Review functions
@app.post(
    "/reviews",
    response_model=ReviewOut,
    status_code=201,
    tags=["리뷰"],
    summary="리뷰 등록",
    description="영화에 리뷰를 등록하고, 감성 분석 결과까지 함께 저장. 영화가 없을 경우 404 반환",
)
def create_review(review: ReviewCreate):
    """리뷰 생성/추가"""
    get_movie(review.movie_id)
    result = analyze(review.text)
    new_id = execute(
        "INSERT INTO reviews (movie_id, author, text, sentiment, sentiment_score) VALUES (?, ?, ?, ?, ?)",
        (
            review.movie_id,
            review.author,
            review.text,
            result["label"],
            result["score"],
        ),
    )
    return fetch_one("SELECT * FROM reviews WHERE id = ?", (new_id,))


@app.get(
    "/reviews",
    response_model=list[ReviewOut],
    tags=["리뷰"],
    summary="리뷰 목록 조회",
    description="리뷰를 최신순으로 조회. limit의 default값은 전체(개수 지정 가능)",
)
def list_reviews(limit: int | None = Query(default=None, ge=1)):
    # GET /reviews?limit=10
    """리뷰 전체 목록"""
    if limit is None:
        return fetch_all("SELECT * FROM reviews ORDER BY created_at DESC, id DESC")
    return fetch_all(
        "SELECT * FROM reviews ORDER BY created_at DESC, id DESC LIMIT ?",
        (limit,),
    )


@app.get(
    "/movies/{movie_id}/reviews",
    response_model=list[ReviewOut],
    tags=["리뷰"],
    summary="특정 영화 리뷰 조회",
    description="해당 영화의 리뷰를 최신순으로 반환. 영화가 없다면 404를, 리뷰가 없다면 빈 목록 반환",
)
def list_movie_reviews(movie_id: int):
    # GET /movies/{movie_id}/reviews
    """특정 영화에 대한 리뷰"""
    get_movie(movie_id)
    rows = fetch_all(
        "SELECT * FROM reviews WHERE movie_id = ? ORDER BY created_at DESC, id DESC",
        (movie_id,),
    )
    return rows


@app.delete(
    "/reviews/{review_id}",
    response_model=ReviewOut,
    tags=["리뷰"],
    summary="리뷰 삭제",
    description="리뷰 ID에 해당하는 리뷰 삭제 및 삭제된 정보 반환. 리뷰가 없을 시 404 반환",
)
def delete_review(review_id: int):
    """리뷰 삭제"""
    review = fetch_one(
        "SELECT * FROM reviews WHERE id = ?",
        (review_id,),
    )
    if review is None:
        raise HTTPException(404, f"해당 리뷰는 존재하지 않습니다")
    execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    return review


# 그 외.
@app.get(
    "/movies/{movie_id}/score",
    response_model=MovieScoreOut,
    tags=["영화"],
    summary="영화 평균 감성 점수 조회",
    description="리뷰 수와 평균 감성 점수를 반환. 리뷰가 없을 경우 평균->null, 영화가 없을 경우 404반환",
)
def get_movie_score(movie_id: int):
    """특정 영화에 대한 리뷰들의 sentiment_score의 평균"""
    get_movie(movie_id)
    row = fetch_one(
        "SELECT COUNT(*) AS count, AVG(sentiment_score) AS average FROM reviews WHERE movie_id = ?",
        (movie_id,),
    )
    average = round(row["average"], 4) if row["average"] is not None else None
    return {"movie_id": movie_id, "count": row["count"], "average": average}


@app.get("/health", tags=["서버"], summary="서버 상태 확인")
def health_check():
    return {"status": "ok"}
