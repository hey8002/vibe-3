from fastapi import APIRouter, HTTPException

from app.schemas.news import NewsCollectRequest, NewsCollectResult
from app.services.news_collector import collect_policy_news
from app.services.news_scheduler import start_news_scheduler
from app.services.news_store import list_news_articles, list_news_jobs, save_news_articles

start_news_scheduler()

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
def list_news(date: str | None = None) -> dict[str, list[dict[str, object]]]:
    return {"items": list_news_articles(date)}


@router.get("/jobs")
def get_news_jobs() -> dict[str, list[dict[str, object]]]:
    return {"items": list_news_jobs()}


@router.post("/collect", response_model=NewsCollectResult)
def collect_news(payload: NewsCollectRequest) -> NewsCollectResult:
    target_date = payload.target_date
    if target_date is None:
        from datetime import datetime, timedelta, timezone

        target_date = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
    try:
        items = collect_policy_news(target_date)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    collected, skipped = save_news_articles(items, target_date)
    return NewsCollectResult(
        target_date=target_date,
        collected=collected,
        skipped=skipped,
        failed=0,
        items=items,
    )
