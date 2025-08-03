from sqlalchemy import Table, Column, Integer, Text, MetaData

metadata = MetaData()

mitigation_suggestion = Table(
    "mitigation_suggestion",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("mitigasi", Text),
    Column("saran", Text),
    Column("category", Text),
    Column("when", Text),
)