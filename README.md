# Mission 18

영화 정보를 등록하고 사용자 리뷰와 감성 분석 결과를 확인하는 웹 서비스입니다.

## 실행 준비

- Python **3.13**을 준비합니다. 확인한 개발 버전은 **3.13.9**입니다.
- 프로젝트를 내려받고, `README.md`, `backend/`, `frontend/`가 있는 **최상위 폴더**를 터미널에서 엽니다.
- 터미널 두 개를 준비합니다. 백엔드와 프론트엔드는 각각 실행한 상태로 유지합니다.
- 함께 제공된 `backend/data/sentiment_model.joblib`이 있어야 합니다.
- 백엔드를 처음 실행하면 빈 데이터베이스가 자동 생성됩니다. 영화 등록 페이지에서 데이터를 추가하세요.

아래 명령은 macOS·Linux의 bash/zsh 기준입니다.

## 처음 실행하기

### 1. 백엔드 - 터미널 A

프로젝트 최상위 폴더에서 실행합니다.

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

`Application startup complete.`가 나오면 준비가 끝납니다.
[서버 상태](http://127.0.0.1:8000/health)를 열어 다음 응답을 확인하세요.

```json
{"status": "ok"}
```

터미널 A를 켜둔 채 다음 단계로 이동합니다.

### 2. 프론트엔드 - 터미널 B

새 터미널을 **프로젝트 최상위 폴더**에서 열고 실행합니다.

```bash
cd frontend
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8501
```

브라우저에서 [영화 리뷰 서비스](http://localhost:8501)를 엽니다.
테마가 적용되도록 `frontend/` 폴더에서 실행하세요.

## 설치 후 다시 실행하기

각 명령 묶음은 **프로젝트 최상위 폴더**에서 시작합니다.

터미널 A:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

터미널 B:

```bash
cd frontend
source .venv/bin/activate
python -m streamlit run app.py --server.port 8501
```

종료할 때는 각 터미널에서 `Ctrl+C`를 누릅니다.

## 사용하기

1. **영화 등록:** 제목, 개봉일, 감독, 장르, 포스터 이미지 URL을 입력하고 등록합니다.
2. **리뷰 등록:** 영화를 선택하고 작성자와 내용을 입력하면 감성 분석 결과가 표시됩니다.
3. **영화 정보 및 리뷰:** 영화 정보, 평균 감성 점수, 최근 리뷰 10개를 확인합니다.

감성 점수는 **긍정일 확률(0~1)**입니다.
API 조회·삭제는 [FastAPI Docs](http://127.0.0.1:8000/docs)에서 실행할 수 있습니다.

## 실행이 안 될 때

- **서버 연결 실패:** 터미널 A가 실행 중인지, 서버 상태 주소가 열리는지 확인합니다.
- **모델 파일 없음:** `backend/data/sentiment_model.joblib` 위치에 제공된 모델 파일을 배치합니다.
- **패키지 오류:** 해당 폴더의 가상환경을 활성화한 뒤 `python -m pip install -r requirements.txt`를 실행합니다.
- **main 모듈 오류:** 백엔드 실행 위치가 `backend/`인지 확인합니다.
- **포트 사용 중:** 이미 실행한 서버를 해당 터미널에서 `Ctrl+C`로 종료합니다.

## Windows에서 실행하기

폴더 이동과 설치·실행 순서는 같습니다. 각 폴더에서 가상환경 생성·활성화 명령만 다음으로 바꿉니다.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

PowerShell에서 활성화가 제한되면 위 안내의 `python` 대신 `.\.venv\Scripts\python.exe`를 사용합니다.
실제 동작을 확인한 개발 환경은 macOS입니다.
