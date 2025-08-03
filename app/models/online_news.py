from sqlalchemy import Table, Column, Integer, Text, MetaData

metadata = MetaData()

online_news = Table(
    "online_news",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("what", Text),
    Column("where", Text),
    Column("who", Text),
    Column("when", Text),
    Column("why", Text),
    Column("how", Text),
    Column("summary", Text),
    Column("category", Text),
    Column("url", Text),
)
