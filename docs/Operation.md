# 공공직군 행정업무 슈퍼앱 운영 문서

## 1. 현재 개발환경 상태

### Frontend
- 위치: `frontend/`
- 설치된 주요 패키지
  - `react`
  - `react-dom`
  - `vite`
  - `typescript`
  - `@vitejs/plugin-react`
  - `@types/react`
  - `@types/react-dom`

### Backend
- 위치: `backend/`
- 가상환경: `backend/.venv`
- Python: `3.14.6`
- 설치된 주요 패키지
  - `fastapi`
  - `uvicorn`

### Database
- SQLite 사용 예정
- 현재 DB 파일은 아직 생성하지 않음

## 2. 실행 준비

### 2.1 Frontend
현재는 모듈만 설치되어 있고 Vite 소스 파일은 아직 생성하지 않았다. 구현 단계에서 `vite.config.ts`, `index.html`, `src/`를 생성한 뒤 아래 명령으로 실행한다.

```powershell
cd frontend
npm run dev
```

### 2.2 Backend
uv 캐시 권한 문제를 피하기 위해 아래 환경변수를 먼저 지정한다.

```powershell
cd backend
$env:UV_CACHE_DIR='..\.uv-cache'
```

가상환경 활성화:

```powershell
.\.venv\Scripts\activate
```

FastAPI 앱 구현 후 실행 예시:

```powershell
uvicorn app.main:app --reload
```

uv를 통해 실행하는 방식:

```powershell
uv run uvicorn app.main:app --reload
```

## 3. 자주 발생하는 에러와 대응

### 3.1 `python` 명령이 Microsoft Store로 연결되는 문제
현상:
```text
Python was not found but can be installed from the Microsoft Store
```

원인:
- Windows App Execution Alias가 `python.exe`를 Microsoft Store stub으로 연결하고 있음

대응:
- 직접 `python` 명령을 사용하지 말고 uv 가상환경의 Python을 사용한다.

```powershell
.\.venv\Scripts\python.exe --version
```

### 3.2 uv 캐시 접근 권한 문제
현상:
```text
Failed to initialize cache at C:\Users\admin\AppData\Local\uv\cache
```

대응:
```powershell
$env:UV_CACHE_DIR='..\.uv-cache'
```

### 3.3 npm 패키지 설치 실패
현상:
```text
cache mode is 'only-if-cached' but no cached response is available
```

원인:
- 네트워크 제한 또는 npm registry 접근 제한

대응:
- 네트워크 접근이 가능한 환경에서 재실행한다.
- 필요 시 사내 프록시 또는 npm registry 설정을 확인한다.

### 3.4 sqlite3 명령어 없음
현상:
```text
sqlite3 is not recognized
```

원인:
- SQLite CLI가 설치되어 있지 않거나 PATH에 없음

대응:
- 앱 개발은 Python 내장 `sqlite3` 모듈로 가능하다.
- 터미널에서 직접 DB를 확인하려면 SQLite CLI를 별도로 설치한다.

## 4. 운영 사용법 초안

### 4.1 팀원 스케줄 관리
- 팀원은 본인 일정을 등록한다.
- 팀 관리자는 팀 전체 일정을 확인한다.
- 일정 유형별 필터로 휴가, 출장, 근무 등을 구분한다.

### 4.2 엑셀 업무 자동화
- 사용자는 엑셀 파일을 업로드한다.
- 분리 작업은 기준 컬럼을 선택한다.
- 병합 작업은 여러 파일을 업로드한다.
- 결과 파일을 다운로드한다.

### 4.3 민원 업무 챗봇
- 관리자는 민원 매뉴얼을 등록한다.
- 담당자는 민원 내용을 질문으로 입력한다.
- 챗봇은 응대 초안을 제공한다.
- 담당자는 최종 답변 전에 반드시 검토한다.

### 4.4 뉴스 기사 수집
- 관리자는 수집 키워드를 등록한다.
- 시스템은 매일 아침 뉴스를 수집한다.
- 사용자는 당일 기사와 요약을 확인한다.

## 5. 백업 대상
- SQLite DB 파일
- 업로드된 민원 매뉴얼
- 엑셀 처리 결과 파일 중 보존 대상
- 환경 설정 파일

## 6. 로그 관리 원칙
- 개인정보와 민원 원문은 로그에 남기지 않는다.
- 오류 로그에는 요청 ID, 발생 시각, API 경로, 오류 유형만 기록한다.
- 파일 처리 오류는 파일명, 시트명, 컬럼명 중심으로 기록한다.

## 7. 배포 전 체크리스트
- FE 빌드 성공 여부 확인
- BE 의존성 잠금 파일 생성 여부 확인
- API 상태 확인 엔드포인트 구현
- SQLite DB 초기화 스크립트 준비
- 파일 업로드 크기 제한 적용
- 민감정보 로그 제외 확인
- 뉴스 수집 실패 재시도 정책 확인

