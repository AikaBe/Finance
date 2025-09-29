import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Подключение к PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:080116bs@localhost:5432/finance_db")

# Загружаем данные
df = pd.read_sql("""
    SELECT 
        TO_CHAR(t.date, 'YYYY-MM') AS month,
        SUM(t.amount) AS total_amount
    FROM trans t
    GROUP BY TO_CHAR(t.date, 'YYYY-MM')
    ORDER BY month
""", engine)

# Приводим месяц к строковому типу
df['month'] = df['month'].astype(str)

# Вариант 1: Scatter с анимацией и нормализованным цветом
fig_scatter = px.scatter(
    df,
    x="month",
    y="total_amount",
    animation_frame="month",
    size_max=30,  # ограничение размера точек
    color="total_amount",
    color_continuous_scale="Viridis",
    title="Сумма транзакций по месяцам (интерактивный ползунок)",
    labels={"month": "Месяц", "total_amount": "Сумма"}
)
fig_scatter.show()

fig_line.show()
