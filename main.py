import psycopg2
import csv

conn = psycopg2.connect(
    dbname="finance_db",
    user="postgres",     
    password="080116bs", 
    host="localhost",
    port="5432"
)

cursor = conn.cursor()
with open("queries.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

queries = [q.strip() for q in sql_script.split(";") if q.strip()]

for i, query in enumerate(queries, start=1):
    print(f"\n--- Results for the query {i} ---")
    cursor.execute(query)
    try:
        rows = cursor.fetchall()
        for row in rows[:10]:
            print(row)

        with open(f"query_{i}.csv", "w", newline="", encoding="utf-8") as f_csv:
            writer = csv.writer(f_csv)
            colnames = [desc[0] for desc in cursor.description]
            writer.writerow(colnames)
            writer.writerows(rows)
    except psycopg2.ProgrammingError:
        print("No data to display")

cursor.close()
conn.close()