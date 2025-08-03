from sqlalchemy import select
from app.models.mitigation import mitigation_suggestion
from app.database import database

async def get_mitigation_table(category: str = None, limit: int = 1000):
    query = select(
        mitigation_suggestion.c.mitigasi,
        mitigation_suggestion.c.saran,
        mitigation_suggestion.c.category,
        mitigation_suggestion.c.when
    ).limit(limit)

    if category:
        query = query.where(mitigation_suggestion.c.category == category)

    return await database.fetch_all(query)
