import os
import sys
import subprocess
import time
from datetime import date
from pathlib import Path

import requests
import streamlit as st

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def backend_is_healthy(_proc=None):
    """백엔드의 정상 응답을 확인. 캐시된 서버의 상태 검사에도 사용"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=1)
        if response.status_code != 200:
            return False
        body = response.json()
        return isinstance(body, dict) and body.get("status") == "ok"
    except (requests.RequestException, ValueError):
        return False


@st.cache_resource(
    show_spinner="서비스 서버 준비 중...",
    validate=backend_is_healthy,
)
def ensure_backend_running():
    """실행 중인 서버를 재사용하거나 새로 실행"""
    if backend_is_healthy():
        return None

    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=backend_dir,
    )

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        exit_code = proc.poll()
        if exit_code is not None:
            raise RuntimeError(
                f"백엔드가 종료되었습니다(종료 코드: {exit_code}). "
                "터미널 또는 배포 로그를 확인해주세요."
            )
        if backend_is_healthy():
            return proc
        time.sleep(0.5)

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    raise RuntimeError("백엔드가 제한 시간 안에 준비되지 않았습니다")


def api_get(path: str, params: dict | None = None):
    """백엔드에 GET 요청을 보내고 JSON 결과를 반환"""
    response = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def render_movies():
    movies = api_get("/movies")
    if not movies:
        st.info("등록된 영화가 없습니다")
        return

    for movie in movies:
        st.subheader(movie["title"])
        st.image(movie["poster_url"], width=200)
        st.write("개봉일:", movie["release_date"])
        st.write("감독:", movie["director"])
        st.write("장르:", movie["genre"])

        score = api_get(f"/movies/{movie['id']}/score")
        st.write(f"리뷰 수: {score['count']}")
        if score["average"] is None:
            st.info("아직 리뷰가 없습니다")
        else:
            st.write(f"평균 감성 점수 (0~1): {score["average"]:.4f}")


def api_post(path: str, payload: dict):
    """백엔드에 JSON 데이터를 POST하고 등록 결과를 반환"""
    response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def render_movie_form():
    """입력한 영화 정보를 FastAPI에 전달해 등록"""
    with st.form("movie_form", clear_on_submit=True):
        st.subheader("영화 등록")
        title = st.text_input(
            "제목",
            value="",
        ).strip()
        release_date = st.date_input(
            "개봉일",
            value=date.today(),
            min_value=date(1900, 1, 1),
        )
        director = st.text_input("감독").strip()
        genre = st.text_input("장르").strip()
        poster_url = st.text_input("포스터").strip()
        submitted = st.form_submit_button("영화 등록")

        if submitted:
            if not all([title, director, genre, poster_url]):
                st.warning("모든 항목을 입력해주세요")
                return

            payload = {
                "title": title,
                "release_date": release_date.isoformat(),
                "director": director,
                "genre": genre,
                "poster_url": poster_url,
            }

            try:
                created_movie = api_post("/movies", payload)
                st.success(f"{created_movie['title']} 등록 완료")
            except requests.RequestException:
                st.error(
                    "영화 등록에 실패하였습니다. 입력값과 서버 연결을 확인해주세요"
                )


def render_review_form():
    """선택한 영화에 리뷰를 등록하고 감성 분석 결과 표시"""
    movies = api_get("/movies")
    if not movies:
        st.warning("해당 영화를 먼저 등록해주세요")
        return
    selected_movie = st.selectbox(
        "영화 선택",
        options=movies,
        format_func=lambda m: m["title"],
    )

    with st.form("review_form", clear_on_submit=True):
        st.subheader("리뷰 등록")
        movie_id = selected_movie["id"]
        author = st.text_input("작성자", value="익명").strip()
        text = st.text_area("내용", value="").strip()
        submitted = st.form_submit_button("리뷰 등록")

    if submitted:
        if not all([movie_id, author, text]):
            st.warning("모든 항목을 입력해주세요")
            return

        payload = {
            "movie_id": movie_id,
            "author": author,
            "text": text,
        }

        try:
            created_reviews = api_post("/reviews", payload)
            st.success("리뷰 등록 완료")
            st.write(f"감성 판단: {created_reviews['sentiment']}")
            st.write(f"긍정 확률(0~1): {created_reviews['sentiment_score']:.4f}")
        except requests.RequestException:
            st.error("리뷰 등록에 실패하였습니다. 입력값과 서버 연결을 확인해주세요")


def render_recent_reviews():
    """최근 리뷰 최대 10개를 표로 조회"""
    reviews = api_get("/reviews", params={"limit": 10})
    if not reviews:
        st.info("리뷰를 등록해 주세요")
        return
    st.subheader(f"최근 리뷰 ({len(reviews)}개)")
    st.dataframe(
        reviews,
        hide_index=True,
        column_order=[
            "movie_id",
            "created_at",
            "author",
            "text",
            "sentiment",
            "sentiment_score",
        ],
        column_config={
            "movie_id": "영화 ID",
            "created_at": "작성일",
            "author": "작성자",
            "text": "내용",
            "sentiment": "감성 판단",
            "sentiment_score": "긍정 확률 (0~1)",
        },
    )


def render_movie_info_reviews():
    """영화 정보와 최근 리뷰 표시"""
    render_movies()
    st.divider()
    render_recent_reviews()


st.title("🎥 영화 리뷰 서비스")

try:
    ensure_backend_running()
except (OSError, RuntimeError) as exc:
    st.error(str(exc))
    st.stop()

page = st.navigation(
    [
        st.Page(render_movie_form, title="영화 등록", default=True),
        st.Page(render_review_form, title="리뷰 등록"),
        st.Page(render_movie_info_reviews, title="영화 정보 및 리뷰"),
    ]
)

try:
    page.run()
except requests.RequestException:
    st.error("서버와 연결하지 못했습니다. 잠시 후 다시 시도해주세요")
