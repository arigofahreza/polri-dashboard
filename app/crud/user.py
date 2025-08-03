from sqlalchemy import select
from app.models.user import dashboard_users
from app.database import database

async def get_user_by_credentials(username: str, password: str):
    query = select(dashboard_users).where(dashboard_users.c.username == username, dashboard_users.c.password == password)
    return await database.fetch_one(query)
