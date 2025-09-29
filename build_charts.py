import os
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

# --- Настройки подключения к PostgreSQL ---
engine = create_engine("postgresql+psycopg2://postgres:080116bs@localhost:5432/finance_db")

# --- Папка для сохранения графиков ---
charts_dir = "charts"
os.makedirs(charts_dir, exist_ok=True)

# --- Чтение запросов из файла ---
queries = []
with open("graph_guery.sql", "r", encoding="utf-8") as f:
    content = f.read()
    blocks = content.split("-- name:")
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        name = lines[0].strip()
        qtype = title = xlabel = ylabel = ""
        sql_lines = []
        for line in lines[1:]:
            if line.startswith("-- type:"):
                qtype = line.split(":")[1].strip()
            elif line.startswith("-- title:"):
                title = line.split(":")[1].strip()
            elif line.startswith("-- xlabel:"):
                xlabel = line.split(":")[1].strip()
            elif line.startswith("-- ylabel:"):
                ylabel = line.split(":")[1].strip()
            elif not line.startswith("--"):
                sql_lines.append(line)
        sql = "\n".join(sql_lines)
        queries.append({
            "name": name,
            "type": qtype,
            "title": title,
            "xlabel": xlabel,
            "ylabel": ylabel,
            "sql": sql
        })

# --- Функция построения и сохранения графиков ---
def plot_graph(df, q):
    if q['type'] in ['bar', 'barh', 'pie', 'line', 'scatter']:
        df = df.dropna(subset=[df.columns[0]])
        
    plt.figure(figsize=(10,6))
    chart_file = os.path.join(charts_dir, f"{q['name']}.png")

    if q['type'] == 'pie':
        plt.pie(df.iloc[:,1], labels=df.iloc[:,0], autopct='%1.1f%%', startangle=140)
        plt.title(q['title'])
        plt.legend(df.iloc[:,0])
    elif q['type'] == 'bar':
        plt.bar(df.iloc[:,0], df.iloc[:,1], color='skyblue')
        plt.title(q['title'])
        plt.xlabel(q['xlabel'])
        plt.ylabel(q['ylabel'])
    elif q['type'] == 'barh':
        plt.barh(df.iloc[:,0], df.iloc[:,1], color='lightgreen')
        plt.title(q['title'])
        plt.xlabel(q['xlabel'])
        plt.ylabel(q['ylabel'])
    elif q['type'] == 'line':
        plt.plot(df.iloc[:,0], df.iloc[:,1], marker='o', linestyle='-', label=q['ylabel'])
        plt.title(q['title'])
        plt.xlabel(q['xlabel'])
        plt.ylabel(q['ylabel'])
        plt.xticks(rotation=45)
        plt.legend()
    elif q['type'] == 'hist':
        plt.hist(df.iloc[:,0], bins=10, color='salmon', edgecolor='black')
        plt.title(q['title'])
        plt.xlabel(q['xlabel'])
        plt.ylabel(q['ylabel'])
    elif q['type'] == 'scatter':
        plt.scatter(df.iloc[:,0], df.iloc[:,1], color='purple')
        plt.title(q['title'])
        plt.xlabel(q['xlabel'])
        plt.ylabel(q['ylabel'])
    else:
        print(f"Unknown chart type: {q['type']}")
        return

    plt.tight_layout()
    plt.savefig(chart_file)
    plt.close()
    
    # --- Консольный отчет ---
    print(f"[{q['name']}] {q['title']}")
    print(f"  Тип графика: {q['type']}")
    print(f"  Количество строк: {len(df)}")
    print(f"  Сохранили график: {chart_file}\n")

# --- Основной цикл ---
for q in queries:
    df = pd.read_sql(q['sql'], engine)
    plot_graph(df, q)

print("Все графики построены и сохранены в папке 'charts/'.")
