from fastapi import APIRouter

router = APIRouter(prefix="/excel", tags=["excel"])


@router.get("/jobs")
def list_excel_jobs() -> dict[str, list[dict[str, str]]]:
    return {"items": []}
