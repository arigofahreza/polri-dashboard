from typing import Optional

from fastapi import APIRouter, Query
from app.crud.investigation import get_category_counts, get_daily_report, get_heatmap_data, get_category_trend, \
    get_latest_investigation, get_wordcloud_data, get_top_contributors, get_top_contributors_trend, \
    get_office_distribution
from app.crud.mitigations import get_mitigation_table
from app.crud.online_news import get_online_news_count, get_table_chart

router = APIRouter(prefix="/chart", tags=['chart'])

@router.get("/category")
async def category_chart(category: Optional[str] = Query(default=None)):
    results = await get_category_counts(category)
    return results

@router.get("/daily")
async def daily_chart(
    limit: int = 500,
    category: Optional[str] = Query(default=None)
):
    return await get_daily_report(limit, category)

@router.get("/heatmap")
async def heatmap_chart(
    limit: int = 10000,
    category: Optional[str] = Query(default=None)
):
    return await get_heatmap_data(limit, category)

@router.get("/trend/category")
async def trend_chart(
    limit: int = 30,
    top_categories: int = 25
):
    return await get_category_trend(limit, top_categories)

@router.get("/investigation-table")
async def latest_table(limit: int = 1000, category: str | None = None):
    return await get_latest_investigation(limit, category)

@router.get("/wordcloud")
async def wordcloud_chart(limit: int = 500, category: str | None = None):
    return await get_wordcloud_data(limit, category)

@router.get("/contributors")
async def top_contributors(
    limit: int = 5,
    category: Optional[str] = Query(default=None)
):
    return await get_top_contributors(limit=limit, category=category)

@router.get("/trend/contributors")
async def trend_contributors_chart():
    return await get_top_contributors_trend()

@router.get("/online-news")
async def online_news_count():
    results = await get_online_news_count()
    return results

@router.get("/online-news-table")
async def table_chart():
    return await get_table_chart()

@router.get("/mitigation-table")
async def mitigation_table_chart(category: Optional[str] = Query(None)):
    return await get_mitigation_table(category)

@router.get("/office-distribution")
async def office_distribution(
    category: Optional[str] = None
):
    return await get_office_distribution(category)