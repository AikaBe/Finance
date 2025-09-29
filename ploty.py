import pandas as pd
import plotly.express as px
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="finance_db",
    user="postgres",
    password="080116bs"
)

query = """
SELECT 
    EXTRACT(YEAR FROM birth_date) AS birth_year,
    COUNT(*) AS clients_count
FROM client
GROUP BY birth_year
ORDER BY birth_year;
"""

df = pd.read_sql(query, conn)

df["decade"] = (df["birth_year"] // 10) * 10

fig = px.scatter(
    df,
    x="birth_year",
    y="clients_count",
    animation_frame="decade", 
    size="clients_count",
    color="clients_count",
    title="Распределение клиентов по годам рождения"
)

fig.show()
