from __future__ import annotations

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    title: str
    published_date: str
    source_url: str
    department: str | None = None
    summary: str | None = None
    content: str | None = None
    collected_at: str


class NewsCollectRequest(BaseModel):
    target_date: str | None = Field(default=None, description="YYYY-MM-DD")


class NewsCollectResult(BaseModel):
    target_date: str
    collected: int
    skipped: int
    failed: int
    items: list[NewsArticle]

