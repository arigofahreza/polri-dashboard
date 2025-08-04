import datetime
from io import BytesIO
from fastapi.responses import FileResponse
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage
from sqlalchemy import text, select, func, and_, desc, cast, Date, insert
from sqlalchemy.orm import aliased

from app.database import database
from app.llm import client
from app.models.investigation import investigation_notes
import pandas as pd
import matplotlib.pyplot as plt

from app.models.mitigation import mitigation_suggestion
from app.models.office import offices
from app.models.online_news import online_news
from app.models.report import report_metadata
from app.models.user import users


async def get_report_data(category: str, start_date: str, end_date: str, title: str = None):
    query = select(investigation_notes).where(
        and_(
            investigation_notes.c.category == category,
            investigation_notes.c.when.between(start_date, end_date)
        )
    )
    investigation_data = await database.fetch_all(query)

    df = pd.DataFrame([dict(row) for row in investigation_data])
    count_df = df.shape[0]
    plot_df = df.groupby('when').size().reset_index(name='jumlah')

    fig, ax = plt.subplots()
    ax.plot(plot_df['when'], plot_df['jumlah'], marker='o')
    ax.set_title("Jumlah Kasus per Hari")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah")
    plt.xticks(rotation=45)
    plt.tight_layout()

    investigation_img_stream = BytesIO()
    plt.savefig(investigation_img_stream, format='png')
    investigation_img_stream.seek(0)

    md_investigation_data = df.to_markdown(index=False)

    response_summary = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan ringkasan dari data berikut:\n{md_investigation_data}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    response_trend = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight trend insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan deskripsi yang menjelaskan dari trend data berikut:\n{md_investigation_data}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    in2 = aliased(investigation_notes)

    query_office_count = (
        select(
            func.count().label("count"),
            offices.c.nama
        )
        .select_from(
            users
            .join(offices, offices.c.id == users.c.kantor_id)
            .join(in2, users.c.no_telepon == in2.c.phone_number)
        )
        .group_by(offices.c.nama)
    )
    office_count = await database.fetch_all(query_office_count)
    df_office = pd.DataFrame([dict(row) for row in office_count])

    md_office = df_office.to_markdown(index=False)
    response_office = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan deskripsi yang menjelaskan dari data berikut:\n{md_office}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df_office["nama"], df_office["count"], color='skyblue')
    ax.set_title("Jumlah Laporan per Lokasi")
    ax.set_xlabel("Lokasi")
    ax.set_ylabel("Jumlah")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    office_img_stream = BytesIO()
    plt.savefig(office_img_stream, format='png')
    office_img_stream.seek(0)

    contributor_query = (
        select(
            users.c.nama.label('name'),
            func.count(investigation_notes.c.id).label("total")
        )
        .select_from(
            investigation_notes.join(users, investigation_notes.c.phone_number == users.c.no_telepon)
        )
        .group_by(users.c.nama)
        .order_by(desc(func.count(investigation_notes.c.id)))
        .limit(5)
    )
    contributor_query = contributor_query.where(investigation_notes.c.category == category)
    contributor_count = await database.fetch_all(contributor_query)

    contributor_df = pd.DataFrame([dict(row) for row in contributor_count])
    md_contributor_df = contributor_df.to_markdown(index=False)

    response_contributor = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan deskripsi yang menjelaskan dari data berikut:\n{md_contributor_df}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(contributor_df["name"], contributor_df["total"], color='lightcoral')

    # Labels and titles
    ax.set_title("Jumlah Laporan per Contributor", fontsize=12)
    ax.set_xlabel("Nama")
    ax.set_ylabel("Total")
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()

    # Step 3: Save as binary image
    contributor_img_stream = BytesIO()
    plt.savefig(contributor_img_stream, format='png')
    contributor_img_stream.seek(0)

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
    daily_data_query = daily_data_query.where(investigation_notes.c.category == category)
    trend_contributor_data = await database.fetch_all(daily_data_query)

    trend_contributor_df = pd.DataFrame([dict(row) for row in trend_contributor_data])
    md_trend_contributor_df = trend_contributor_df.to_markdown(index=False)

    response_trend_contributor = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan deskripsi yang menjelaskan trend dari data berikut:\n{md_trend_contributor_df}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    trend_contributor_df["date"] = pd.to_datetime(trend_contributor_df["date"])

    # Step 2: Create line chart
    fig, ax = plt.subplots(figsize=(8, 4))

    # Plot line for each person
    for name, group in trend_contributor_df.groupby("name"):
        group_sorted = group.sort_values("date")
        ax.plot(group_sorted["date"], group_sorted["count"], marker="o", label=name)

    # Set labels and title
    ax.set_title("Tren Jumlah Laporan per Nama")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah Laporan")
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=30)
    plt.tight_layout()

    trend_contrbutor_img_stream = BytesIO()
    plt.savefig(trend_contrbutor_img_stream, format='png')
    trend_contrbutor_img_stream.seek(0)

    query_online_news = select(online_news).where(
        and_(
            online_news.c.category == category,
            online_news.c.when.between(start_date, end_date)
        )
    )
    online_news_data = await database.fetch_all(query_online_news)

    online_news_df = pd.DataFrame([dict(row) for row in online_news_data])
    md_online_news = online_news_df.to_markdown(index=False)

    count_online_news_df = online_news_df.shape[0]
    response_online_news = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan ringkasan dari data berikut:\n{md_online_news}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    query_mitigation = select(mitigation_suggestion).where(
        and_(
            mitigation_suggestion.c.category == category,
            mitigation_suggestion.c.when.between(start_date, end_date)
        )
    )
    mitigation_data = await database.fetch_all(query_mitigation)
    df_mitigation_data = pd.DataFrame([dict(row) for row in mitigation_data])
    md_mitigation = df_mitigation_data.to_markdown(index=False)
    response_mitigation = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan insight insiden berdasarkan data yang diberikan."},
            {"role": "user",
             "content": f"Berikan ringkasan dari data berikut:\n{md_mitigation}. buat dalam bentuk 1 paragraf text"}
        ],
        temperature=0.5
    )

    doc = DocxTemplate("./app/template/template-report.docx")
    context = {
        'title': title if title else 'Laporan',
        'kategori': category,
        'generated_date_start': start_date,
        'generated_date_end': end_date,
        'total_report': count_df,
        'chart_tren_laporan': InlineImage(doc, investigation_img_stream, width=Mm(160)),
        'deskripsi_tren_laporan': response_trend.choices[0].message.content,
        'chart_laporan_lokasi': InlineImage(doc, office_img_stream, width=Mm(160)),
        'deskripsi_laporan_perlokasi': response_office.choices[0].message.content,
        'rangkuman_laporan': response_summary.choices[0].message.content,
        'chart_top_kontributor': InlineImage(doc, contributor_img_stream, width=Mm(160)),
        'deskripsi_top_kontributor': response_contributor.choices[0].message.content,
        'chart_tren_kontributor': InlineImage(doc, trend_contrbutor_img_stream, width=Mm(160)),
        'deskripsi_tren_kontributor': response_trend_contributor.choices[0].message.content,
        'total_online_news': count_online_news_df,
        'rangkuman_online_news': response_online_news.choices[0].message.content,
        'mitigasi_saran_online_news': response_mitigation.choices[0].message.content
    }
    doc.render(context)
    filename = f'report-{category}-{start_date}-{end_date}.docx'
    doc.save(f"./app/report/{filename}")
    stmt = (
        insert(report_metadata)
        .values(
            title=filename,
            category=category,
            url=f"https://polda-be.laice.tech/{filename}",
        )
        .returning(report_metadata.c.id)
    )

    inserted_id = await database.fetch_val(stmt)
    return {
        'id': inserted_id,
        'title': filename
    }


async def get_download_report(id: int, url: str):
    query = select(report_metadata).where(
        and_(
            report_metadata.c.id == id,
        )
    )
    report_data = await database.fetch_one(query)
    url_data = report_data['url']
    if url_data != url:
        return {}
    filename = report_data["title"]
    return FileResponse(
        path=f'./app/report/{filename}',
        filename=filename,
        media_type='application/octet-stream'
    )


async def get_all_document(page: int = 1, limit: int = 10):
    offset = (page - 1) * limit

    query = (
        select(report_metadata)
        .order_by(desc(report_metadata.c.id))
        .limit(limit)
        .offset(offset)
    )

    results = await database.fetch_all(query)

    count_query = select(func.count()).select_from(report_metadata)
    total = await database.fetch_val(count_query)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_page": (total + limit - 1) // limit,
        "data": [dict(row) for row in results]
    }