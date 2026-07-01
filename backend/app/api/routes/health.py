from fastapi import APIRouter

from app.core.database import check_database_connection

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "fastapi",
        "message": "FastAPI 서버가 정상 응답했습니다.",
    }


@router.get("/db/health")
def database_health_check() -> dict[str, str]:
    database_path = check_database_connection()

    return {
        "status": "ok",
        "database": str(database_path),
        "message": "SQLite 연결과 쓰기 확인이 완료되었습니다.",
    }
