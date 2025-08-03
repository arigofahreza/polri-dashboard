from sqlalchemy import Table, Column, Integer, String, Text, DateTime, MetaData, func

metadata = MetaData()

report_metadata = Table(
    'report_metadata', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', Text, nullable=False),
    Column('category', String(100)),
    Column('url', Text),
    Column('generated_at', DateTime, default=func.now())
)
