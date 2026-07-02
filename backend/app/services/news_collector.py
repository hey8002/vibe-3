from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.korea.kr"
LIST_URL = "https://www.korea.kr/news/policyNewsList.do"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
}


@dataclass(frozen=True)
class CollectedArticle:
    title: str
    published_date: str
    source_url: str
    department: str | None
    summary: str | None
    content: str | None
    collected_at: str


def _parse_date(text: str | None) -> str:
    if not text:
        return ""
    match = re.search(r"(20\d{2})[.\-/](\d{2})[.\-/](\d{2})", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return ""


def _clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _fetch(url: str, *, params: dict[str, str] | None = None) -> str:
    response = requests.get(url, params=params, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def _extract_article_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[tuple[str, str, str]] = []
    for anchor in soup.select("a[href*='policyNewsView.do']"):
        href = anchor.get("href")
        title_node = anchor.select_one("strong")
        title = _clean_text(title_node.get_text(" ", strip=True) if title_node else None)
        published_date = ""
        img = anchor.select_one("img[src]")
        if img and img.get("src"):
            published_date = _parse_date(img["src"].replace("/", "."))
        if not published_date:
            published_date = _parse_date(anchor.get_text(" ", strip=True))
        if not href or not title or title == "검색기간":
            continue
        links.append((urljoin(BASE_URL, href), title, published_date))
    seen: set[str] = set()
    unique: list[tuple[str, str, str]] = []
    for href, title, published_date in links:
        if href in seen:
            continue
        seen.add(href)
        unique.append((href, title, published_date))
    return unique


def _parse_detail(html: str, source_url: str, fallback_title: str) -> CollectedArticle:
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one("h1")
    title = _clean_text(title_node.get_text(" ", strip=True) if title_node else None) or fallback_title
    published_date = ""
    for candidate in soup.stripped_strings:
        date_value = _parse_date(candidate)
        if date_value:
            published_date = date_value
            break
    if not published_date:
        published_date = ""
    department = None
    for selector in [".author", ".department", ".origin", ".source", ".writer"]:
        node = soup.select_one(selector)
        if node:
            department = _clean_text(node.get_text(" ", strip=True))
            if department:
                break
    content_node = soup.select_one(".article-body, .cont_body, .articleView, .view_cont, #contents")
    content = _clean_text(content_node.get_text(" ", strip=True)) if content_node else None
    summary = None
    summary_node = soup.select_one(".summary, .article-summary, .lead, .sub_title")
    if summary_node:
        summary = _clean_text(summary_node.get_text(" ", strip=True))
    if not published_date:
        published_date = date.today().isoformat()
    return CollectedArticle(
        title=title,
        published_date=published_date,
        source_url=source_url,
        department=department,
        summary=summary,
        content=content,
        collected_at=datetime.now(timezone.utc).isoformat(),
    )


def collect_policy_news(target_date: str) -> list[dict[str, object]]:
    target = date.fromisoformat(target_date)
    page = 1
    collected: list[dict[str, object]] = []
    while page <= 5:
        html = _fetch(LIST_URL, params={"pageIndex": str(page)})
        links = _extract_article_links(html)
        if not links:
            break
        page_matched = False
        for source_url, title, published_date in links:
            if published_date and published_date != target.isoformat():
                continue
            detail_html = _fetch(source_url)
            article = _parse_detail(detail_html, source_url, title)
            if article.published_date != target.isoformat():
                continue
            collected.append(article.__dict__)
            page_matched = True
        if not page_matched:
            # Listings are sorted newest first. If the current page has no matches,
            # the older pages are unlikely to match the same target date.
            break
        page += 1
    return collected


def collect_yesterday_policy_news() -> list[dict[str, object]]:
    yesterday = (datetime.now(timezone(timedelta(hours=9))).date() - timedelta(days=1)).isoformat()
    return collect_policy_news(yesterday)
