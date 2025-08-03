from io import BytesIO

from sqlalchemy import text, select, func, and_
from app.database import database
from app.models.investigation import investigation_notes
import pandas as pd
import matplotlib.pyplot as plt


async def get_report_data(category: str, start_date: str, end_date: str):
    query = select(investigation_notes).where(
        and_(
            investigation_notes.c.category == category,
            investigation_notes.c.when.between(start_date, end_date)
        )
    )
    investigation_data = await database.fetch_all(query)

    df = pd.DataFrame(investigation_data)

    # Count per region (you can modify this to group by date, etc.)
    plot_df = df.groupby('when').size().reset_index(name='jumlah')

    # Plot
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



