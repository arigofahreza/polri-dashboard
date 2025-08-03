from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from app.database import metadata

dashboard_users = Table(
    "dashboard_users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
)

# Tabel: users
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nama", String(100), nullable=False),
    Column("email", String(100), nullable=False),
    Column("no_telepon", String(20), nullable=False),
    Column("kantor_id", Integer, ForeignKey("offices.id")),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
)
