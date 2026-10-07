## API 안내

- `GET /health`: 서버 상태 확인
- `POST /movies`: 영화 등록, 성공 시 `201`
- `GET /movies`: 영화 전체 목록 조회
- `GET /movies/{movie_id}`: 특정 영화 조회
- `DELETE /movies/{movie_id}`: 영화와 연결된 리뷰 삭제, 삭제된 영화 반환
- `POST /reviews`: 리뷰 등록·감성 분석·저장, 성공 시 `201`
- `GET /reviews`: 전체 리뷰를 최신순으로 조회
- `GET /reviews?limit=10`: 최근 리뷰 최대 10개 조회
- `GET /movies/{movie_id}/reviews`: 특정 영화의 리뷰 조회
- `DELETE /reviews/{review_id}`: 리뷰 삭제, 삭제된 리뷰 반환
- `GET /movies/{movie_id}/score`: 리뷰 수와 평균 감성 점수 조회

등록된 영화·리뷰가 없으면 해당 단건 조회·삭제 요청은 `404`를 반환<br>
입력값이 요청 스키마와 맞지 않으면 `422`를 반환

영화 등록 요청 필드: `title`, `release_date`, `director`, `genre`, `poster_url`
리뷰 등록 요청 필드: `movie_id`, `author`, `text`

## 모델과 데이터

### 운영 모델

한국어 영화 리뷰를 문자 **TF-IDF**로 벡터화하고 **로지스틱 회귀**로 분류<br>
학습 데이터: [NSMC](https://github.com/e9t/nsmc)

- TF-IDF: `analyzer="char_wb"`, `ngram_range=(2, 4)`, `min_df=3`, `max_features=50000`, `sublinear_tf=True`
- 로지스틱 회귀: `C=4`, `max_iter=1000`
- 파일 저장: `joblib.dump(..., compress=3)`
- 학습 데이터: 결측값 제거 후 **29,999건**
- 최종 평가 데이터: **5,000건**
- 측정한 최종 평가 정확도: **84.80%**
- 측정한 운영 모델 파일 크기: **약 0.82MB**

CSV:`document`(리뷰 내용) `label`(`0`=부정, `1`=긍정), `split`(`train`/`test`)

### 특징 수를 줄인 비교 실험

학습 데이터 안에서 학습 **23,999건**과 검증 **6,000건**을 나누고,
같은 분할과 나머지 설정을 사용해 최대 특징 수만 비교

- **50,000개:** 검증 정확도 84.7333%, 학습 1.368초, 파일 0.8161MB
- **20,000개:** 검증 정확도 83.9167%, 학습 1.172초, 파일 0.3314MB

특징 수 감소 &rarr; 파일 크기: 약 **59.4% 감소** | 검증 정확도: 약 **0.82%p 감소**
현재 서비스에는 파일 크기와 검증 정확도를 함께 고려하여 **50,000개 설정** 사용
