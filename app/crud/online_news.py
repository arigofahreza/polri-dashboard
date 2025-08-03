from sqlalchemy import func, select, text, desc
from app.models.online_news import online_news
from app.database import database


async def get_online_news_count():
    query = select(func.count()).select_from(online_news).limit(50000)
    return await database.fetch_all(query)

async def get_table_chart(limit: int, category: str = None):
    base_query = select(
        online_news.c.category.label("what"),
        online_news.c.category.label("category"),
        online_news.c.when.label("when"),
        online_news.c.url
    )

    if category:
        base_query = base_query.where(online_news.c.category == category)

    base_query = base_query.order_by(online_news.c.category, desc(online_news.c.when)).limit(limit)

    return await database.fetch_all(base_query)
