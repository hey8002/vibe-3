# 공공직군 행정업무 슈퍼앱 아키텍처

## 1. 기술 스택
- Frontend: TypeScript, Vite, React
- Backend: Python, FastAPI, uv
- Database: SQLite
- Package Management
  - FE: npm
  - BE: uv

## 2. 전체 구조
```text
day3_rpa/
  frontend/
    package.json
    package-lock.json
    node_modules/
  backend/
    .venv/
  docs/
    PRD.mdj
    Architecture.md
    Operation.md
    index.html
```

## 3. 권장 프로젝트 구조
아래 구조는 실제 구현 단계에서 생성할 권장 구조이다.

```text
frontend/
  src/
    app/
    pages/
    features/
      schedule/
      excel/
      chatbot/
      news/
    shared/
      api/
      components/
      types/
      utils/
  index.html
  vite.config.ts
  tsconfig.json

backend/
  app/
    main.py
    core/
      config.py
      database.py
    api/
      routes/
        schedules.py
        excel.py
        chatbot.py
        news.py
    models/
    schemas/
    services/
      schedule_service.py
      excel_service.py
      chatbot_service.py
      news_service.py
    repositories/
    jobs/
      news_collector.py
  data/
    app.db
  uploads/
  pyproject.toml
  uv.lock
```

## 4. 모듈별 역할

### 4.1 Frontend
- 사용자 화면 구성
- API 호출
- 캘린더, 파일 업로드, 챗봇, 뉴스 목록 UI 제공
- 사용자 입력 검증

### 4.2 Backend
- REST API 제공
- 비즈니스 로직 처리
- 파일 업로드 처리
- 엑셀 분리 및 병합 처리
- SQLite 데이터 읽기와 쓰기
- 뉴스 수집 작업 실행
- 민원 매뉴얼 기반 챗봇 응답 처리

### 4.3 Database
SQLite는 초기 MVP에서 단일 파일 DB로 사용한다.

#### 주요 테이블 후보
- `users`: 팀원 정보
- `schedules`: 일정 정보
- `news_articles`: 수집 뉴스
- `chat_manuals`: 민원 매뉴얼 메타데이터
- `chat_messages`: 챗봇 질의응답 기록
- `excel_jobs`: 엑셀 처리 작업 이력

## 5. API 설계 초안

### 5.1 Schedule API
- `GET /api/schedules`: 일정 목록 조회
- `POST /api/schedules`: 일정 등록
- `GET /api/schedules/{schedule_id}`: 일정 상세 조회
- `PUT /api/schedules/{schedule_id}`: 일정 수정
- `DELETE /api/schedules/{schedule_id}`: 일정 삭제

### 5.2 Excel API
- `POST /api/excel/split`: 엑셀 파일 분리
- `POST /api/excel/merge`: 엑셀 파일 병합
- `GET /api/excel/jobs/{job_id}`: 작업 상태 조회
- `GET /api/excel/jobs/{job_id}/download`: 결과 파일 다운로드

### 5.3 Chatbot API
- `POST /api/chatbot/manuals`: 민원 매뉴얼 업로드
- `GET /api/chatbot/manuals`: 매뉴얼 목록 조회
- `POST /api/chatbot/messages`: 질문 전송 및 답변 생성

### 5.4 News API
- `GET /api/news`: 뉴스 목록 조회
- `POST /api/news/collect`: 뉴스 수집 수동 실행
- `GET /api/news/keywords`: 수집 키워드 조회
- `POST /api/news/keywords`: 수집 키워드 등록

## 6. 데이터 흐름

### 6.1 일정 관리
1. 사용자가 캘린더에서 일정 등록
2. FE가 Backend API 호출
3. Backend가 일정 데이터 검증
4. SQLite에 저장
5. FE가 최신 일정 목록 갱신

### 6.2 엑셀 자동화
1. 사용자가 엑셀 파일 업로드
2. Backend가 파일 확장자와 크기 검증
3. 서비스 모듈이 분리 또는 병합 처리
4. 결과 파일을 임시 저장소에 저장
5. 사용자가 결과 파일 다운로드

### 6.3 민원 챗봇
1. 관리자가 민원 매뉴얼 등록
2. Backend가 매뉴얼을 저장하고 검색 가능한 형태로 준비
3. 사용자가 질문 입력
4. Backend가 매뉴얼 기반 답변 생성
5. FE가 답변과 참고 근거 표시

### 6.4 뉴스 수집
1. 스케줄러 또는 수동 API로 수집 실행
2. Backend가 키워드 기준으로 뉴스 검색
3. 중복 제거 후 SQLite 저장
4. FE가 최신 뉴스 목록 표시

## 7. 보안 및 데이터 정책
- 업로드 파일은 허용된 확장자만 처리한다.
- 민감정보는 로그에 기록하지 않는다.
- 챗봇 답변은 최종 행정 판단이 아닌 초안으로 표시한다.
- 외부 뉴스 수집 시 요청 빈도를 제한한다.
- SQLite DB 파일과 업로드 폴더는 백업 대상에 포함한다.

## 8. 기술적 의사결정
- FastAPI는 REST API와 파일 업로드 처리에 적합하다.
- uv는 Python 가상환경과 의존성 관리를 일관되게 유지한다.
- SQLite는 초기 MVP의 설치와 운영 부담을 낮춘다.
- Vite와 React는 빠른 개발 서버와 컴포넌트 기반 UI 구현에 적합하다.

