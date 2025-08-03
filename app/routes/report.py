from typing import Optional

from fastapi import APIRouter, Query
from app.crud.report import get_report_data

router = APIRouter(prefix="/report", tags=['report'])


@router.get("/generate")
async def category_chart(category: str = Query(), start_date: str = Query(), end_date: str = Query(),
                         title: str = Query(default=None)):
    results = await get_report_data(category, start_date, end_date, title)
    return results
