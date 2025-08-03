from typing import Optional

from sqlalchemy import select, func, cast, text, desc
from sqlalchemy.orm import aliased

from app.models.investigation import investigation_notes
from app.models.user import users
from app.models.office import offices
from sqlalchemy.types import Date
from app.database import database


async def get_category_counts(category: str = None):
    if category:
        query = select(
            investigation_notes.c.category,
            func.count().label("count")
        ).where(investigation_notes.c.category == category).group_by(investigation_notes.c.category)
    else:
        query = select(
            func.count().label("count")
        ).select_from(investigation_notes)

    return await database.fetch_all(query)


async def get_category_group_counts():
    query = select(
        investigation_notes.c.category,
        func.count().label("count")
    ).group_by(investigation_notes.c.category)
    return await database.fetch_all(query)


async def get_daily_report(limit: int = 500, category: str = None):
    base_query = select(
        investigation_notes.c.when.label("when"),
        func.count().label("total")
    )

    if category:
        base_query = base_query.where(investigation_notes.c.category == category)

    base_query = base_query.group_by(investigation_notes.c.when)
    base_query = base_query.order_by(func.count().desc()).limit(limit)

    return await database.fetch_all(base_query)


async def get_heatmap_data(limit: int = 10000, category: str = None):
    day = func.extract('day', cast(investigation_notes.c.when, Date)).label("hari")
    month = func.extract('month', cast(investigation_notes.c.when, Date)).label("bulan")
    count = func.count().label("count")

    query = select(day, month, count)

    if category:
        query = query.where(investigation_notes.c.category == category)

    query = query.group_by(day, month)
    query = query.order_by(day.asc(), month.asc())
    query = query.limit(limit)

    return await database.fetch_all(query)


async def get_category_trend(limit: int = 30, top_categories: int = 25):
    # Subquery untuk top categories
    subquery = (
        select(
            investigation_notes.c.category.label("category__"),
            func.count().label("inner_count")
        )
        .group_by(investigation_notes.c.category)
        .order_by(desc("inner_count"))
        .limit(top_categories)
        .alias("series_limit")
    )

    # Join dengan notes
    join_stmt = investigation_notes.join(
        subquery, investigation_notes.c.category == subquery.c.category__
    )

    query = (
        select(
            investigation_notes.c.when,
            investigation_notes.c.category,
            func.count().label("count")
        )
        .select_from(join_stmt)
        .group_by(investigation_notes.c.when, investigation_notes.c.category)
        .order_by(desc("count"))
        .limit(limit)
    )

    return await database.fetch_all(query)


async def get_latest_investigation(limit: int = 1000, category: str | None = None):
    subquery = (
        select(
            investigation_notes.c.what,
            investigation_notes.c.category,
            investigation_notes.c.when,
            investigation_notes.c.id
        )
        .distinct(investigation_notes.c.what)
        .order_by(investigation_notes.c.what, investigation_notes.c.id.desc())
        .subquery()
    )

    query = (
        select(
            subquery.c.what,
            subquery.c.category,
            subquery.c.when
        )
        .order_by(subquery.c.id.desc())
        .limit(limit)
    )

    if category:
        query = query.where(subquery.c.category == category)

    final_query = (
        select(
            query.c.what,
            query.c.category,
            query.c.when
        )
        .limit(limit)
    )

    return await database.fetch_all(final_query)


async def get_wordcloud_data(limit: int = 500, category: str | None = None):
    query = (
        select(
            investigation_notes.c.why.label("why"),
            func.count().label("count")
        )
        .group_by(investigation_notes.c.why)
        .order_by(desc("count"))
        .limit(limit)
    )

    if category:
        query = query.where(investigation_notes.c.category == category)

    return await database.fetch_all(query)


async def get_top_contributors(limit: int = 5, category: Optional[str] = None):
    query = (
        select(
            users.c.nama.label('name'),
            func.count(investigation_notes.c.id).label("total")
        )
        .select_from(
            investigation_notes.join(users, investigation_notes.c.phone_number == users.c.no_telepon)
        )
        .group_by(users.c.nama)
        .order_by(desc(func.count(investigation_notes.c.id)))
        .limit(limit)
    )

    if category:
        query = query.where(investigation_notes.c.category == category)

    return await database.fetch_all(query)


async def get_top_contributors_trend(category: Optional[str] = None):
    top_contributors_subq = (
        select(investigation_notes.c.phone_number)
        .group_by(investigation_notes.c.phone_number)
        .order_by(func.count().desc())
        .limit(5)
        .subquery()
    )

    daily_data_query = (
        select(
            users.c.nama.label('name'),
            investigation_notes.c.category,
            cast(investigation_notes.c.created_at, Date).label("date"),
            func.count().label("count")
        )
        .select_from(
            investigation_notes.join(users, investigation_notes.c.phone_number == users.c.no_telepon)
        )
        .where(investigation_notes.c.phone_number.in_(select(top_contributors_subq.c.phone_number)))
        .group_by(
            users.c.nama,
            investigation_notes.c.category,
            cast(investigation_notes.c.created_at, Date)
        )
        .order_by("date")
    )
    if category:
        daily_data_query = daily_data_query.where(investigation_notes.c.category == category)

    return await database.fetch_all(daily_data_query)


async def get_office_distribution(category: Optional[str] = None):
    # Aliases for joins
    u = aliased(users)
    o = aliased(offices)

    # Subquery
    subq = (
        select(
            investigation_notes.c.id.label('id'),
            u.c.kantor_id.label("kantor_id"),
            u.c.nama.label("anggota"),
            o.c.nama.label("office"),
            o.c.latitude.label("latitude"),
            o.c.longitude.label("longitude")
        )
        .join(u, u.c.no_telepon == investigation_notes.c.phone_number)
        .join(o, o.c.id == u.c.kantor_id)
    )

    if category:
        subq = subq.where(investigation_notes.c.category == category)

    subq = subq.subquery("virtual_table")

    # Main query
    query = (
        select(
            subq.c.office,
            func.count(subq.c.id).label("COUNT(id)")
        )
        .group_by(subq.c.office)
        .order_by(func.count(subq.c.id).desc())
        .limit(1000)
    )

    return await database.fetch_all(query)
