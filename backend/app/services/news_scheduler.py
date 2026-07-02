from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.news_collector import collect_yesterday_policy_news
from app.services.news_store import save_news_articles

_scheduler: BackgroundScheduler | None = None


def start_news_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        _run_daily_collection,
        trigger="cron",
        hour=9,
        minute=0,
        id="policy_news_daily_collect",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler


def _run_daily_collection() -> None:
    items = collect_yesterday_policy_news()
    if items:
        save_news_articles(items, items[0]["published_date"])

