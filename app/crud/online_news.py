from sqlalchemy import func, select, text
from app.models.online_news import online_news
from app.database import database


async def get_online_news_count():
    query = select(func.count()).select_from(online_news).limit(50000)
    return await database.fetch_all(query)

async def get_table_chart():
    query = text("""
        SELECT what AS what, category AS category, "when" AS "when"
        FROM (
            SELECT DISTINCT ON (category) what, category, "when", url
            FROM online_news
            ORDER BY category, "when" DESC
        ) AS virtual_table
        LIMIT 1000;
    """)
    return await database.fetch_all(query)
