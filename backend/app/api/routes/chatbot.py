from fastapi import APIRouter

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.get("/manuals")
def list_manuals() -> dict[str, list[dict[str, str]]]:
    return {"items": []}
