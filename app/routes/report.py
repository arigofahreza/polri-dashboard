from typing import Optional

from fastapi import APIRouter, Query
from app.crud.report import get_report_data, get_download_report, get_all_document

router = APIRouter(prefix="/report", tags=['report'])


@router.get("/generate")
async def generate_report(category: str = Query(), start_date: str = Query(), end_date: str = Query(),
                          title: str = Query(default=None)):
    results = await get_report_data(category, start_date, end_date, title)
    return results


@router.get('/download')
async def download_report(id: int = Query(), url: str = Query()):
    results = await get_download_report(id, url)
    return results


@router.get('/get-all')
async def get_all_report(page: int = Query(), limit: int = Query()):
    results = await get_all_document(page, limit)
    return results
