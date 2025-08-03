from io import BytesIO

from sqlalchemy import text, select, func, and_
from sqlalchemy.orm import aliased

from app.database import database
from app.llm import client
from app.models.investigation import investigation_notes
import pandas as pd
import matplotlib.pyplot as plt

from app.models.office import offices
from app.models.user import users


async def get_report_data(category: str, start_date: str, end_date: str):
    query = select(investigation_notes).where(
        and_(
            investigation_notes.c.category == category,
            investigation_notes.c.when.between(start_date, end_date)
        )
    )
    investigation_data = await database.fetch_all(query)

    df = pd.DataFrame(investigation_data)

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
             "content": "Kamu adalah analis intelijen yang memberikan ringkasan insiden berdasarkan data yang diberikan."},
            {"role": "user", "content": f"Berikan ringkasan dari data berikut:\n{md_investigation_data}"}
        ],
        temperature=0.5
    )

    response_trend = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system",
             "content": "Kamu adalah analis intelijen yang memberikan deskripsi trend insiden berdasarkan data yang diberikan."},
            {"role": "user", "content": f"Berikan deskripsi yang menjelaskan dari trend data berikut:\n{md_investigation_data}"}
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
    office_count = await database.fetch_all(query)
    df_office = pd.DataFrame(office_count)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(df["nama"], df["count"], color='skyblue')
    ax.set_title("Jumlah Laporan per Lokasi")
    ax.set_xlabel("Lokasi")
    ax.set_ylabel("Jumlah")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    office_img_stream = BytesIO()
    plt.savefig(office_img_stream, format='png')
    office_img_stream.seek(0)





