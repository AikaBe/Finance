# geo_fill_improved.py
from geopy.geocoders import Nominatim
import psycopg2
import time
import re

# Параметры подключения — проверь их
conn = psycopg2.connect(
    dbname="finance_db",
    user="postgres",
    password="080116bs",
    host="localhost",
    port="5433"
)

cur = conn.cursor()
geolocator = Nominatim(user_agent="superset_geo_improved", timeout=10)

# Список больших городов Казахстана, чтобы их правильно геокодить
kazakh_cities = {"Almaty", "Astana", "Karaganda", "Shymkent", "Pavlodar"}

# Функция очистки названий: убираем слова-указатели и лишние символы
def clean_name(name):
    if not name:
        return ""
    s = str(name)
    # remove common words in your dataset (lowercase for match)
    s = re.sub(r"\b(mesto|venkov|jih|sever|vychod|zapad|central|north|south|east|west)\b", " ", s, flags=re.IGNORECASE)
    s = s.replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Получаем строки без координат
cur.execute("""
    SELECT district_id, A2, A3
    FROM district
    WHERE latitude IS NULL OR longitude IS NULL
""")
rows = cur.fetchall()
print(f"Найдено {len(rows)} строк без координат.")

def try_geocode_variants(a2, a3):
    """Попробовать несколько вариантов запроса, вернуть (lat, lon) или None."""
    a2_clean = clean_name(a2)
    a3_clean = clean_name(a3)

    # Определяем страну и country_codes (по A2 или по A3)
    if a2 and a2.strip() in kazakh_cities:
        country = "Kazakhstan"
        country_code = "kz"
    else:
        country = "Czechia"  # или "Czech Republic"
        country_code = "cz"

    # Список шаблонов: более специфичные идут сначала
    candidates = []
    if a2_clean and a3_clean:
        candidates.append(f"{a2_clean}, {a3_clean}, {country}")
        candidates.append(f"{a2_clean} {a3_clean}, {country}")
    if a2_clean:
        candidates.append(f"{a2_clean}, {country}")
        candidates.append(f"{a2_clean}")
    if a3_clean:
        candidates.append(f"{a3_clean}, {country}")

    # также попробуем англ./локализованные варианты (вариативно)
    candidates.append(f"{a2_clean}, {country}")
    candidates.append(f"{a2_clean} {country}")
    # убираем дубли
    seen = set()
    candidates = [c for c in candidates if c and (c not in seen and not seen.add(c))]

    for q in candidates:
        try:
            # используем country_codes чтобы ускорить и сузить поиск
            loc = geolocator.geocode(q, country_codes=country_code, exactly_one=True)
            if loc:
                return (loc.latitude, loc.longitude, q)
        except Exception as e:
            # логируем и пробуем далее (не падаем)
            print(f"[ERROR geocode] {q} -> {e}")
            time.sleep(1)
    return None

for district_id, a2, a3 in rows:
    # Пропускаем, если нет A2 и A3
    if not a2 and not a3:
        print(f"[SKIP] {district_id} (no names)")
        continue

    # Попытка геокодирования
    res = try_geocode_variants(a2, a3)
    if res:
        lat, lon, used_query = res
        cur.execute(
            "UPDATE district SET latitude = %s, longitude = %s WHERE district_id = %s",
            (lat, lon, district_id)
        )
        conn.commit()
        print(f"[OK] {district_id}: {a2}, {a3} -> {lat:.5f},{lon:.5f}  (q: {used_query})")
    else:
        # Дополнительная попытка: попробуем только A2 с country 'Czech Republic' (полное название)
        fallback_q = None
        if a2:
            fallback_q = f"{clean_name(a2)}, Czech Republic"
            try:
                loc = geolocator.geocode(fallback_q, country_codes='cz', exactly_one=True)
                if loc:
                    lat, lon = loc.latitude, loc.longitude
                    cur.execute(
                        "UPDATE district SET latitude = %s, longitude = %s WHERE district_id = %s",
                        (lat, lon, district_id)
                    )
                    conn.commit()
                    print(f"[OK-fallback] {district_id}: {a2}, {a3} -> {lat:.5f},{lon:.5f}  (q: {fallback_q})")
                    time.sleep(1)
                    continue
            except Exception as e:
                print(f"[ERROR fallback] {fallback_q} -> {e}")

        # Если всё ещё не найдено — логируем
        print(f"[NOT FOUND] {district_id}: {a2}, {a3}")
    # Небольшая задержка между запросами, соблюдаем правила Nominatim
    time.sleep(1.2)

cur.close()
conn.close()
print("Готово ✅")
