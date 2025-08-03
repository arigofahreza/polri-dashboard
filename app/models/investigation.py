from sqlalchemy import Table, Column, Integer, String, Text, Float, Boolean, TIMESTAMP
from app.database import metadata

investigation_notes = Table(
    "investigation_notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("what", Text),
    Column("when", Text),
    Column("where", Text),
    Column("why", Text),
    Column("who", Text),
    Column("how", Text),
    Column("category", String(100)),
    Column("summary", Text),
    Column("created_at", TIMESTAMP),
    Column("phone_number", String),
    Column("sender_name", String),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("active", Boolean),
)
