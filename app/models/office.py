from sqlalchemy import Table, Column, Integer, MetaData, String, Float, DateTime

metadata = MetaData()

offices = Table(
    "offices",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nama", String(100), nullable=False),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
)

