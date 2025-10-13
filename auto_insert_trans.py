import random
import time
from datetime import datetime, date, timedelta
from decimal import Decimal
import psycopg2

conn = psycopg2.connect(
    dbname="finance_db",
    user="postgres",
    password="080116bs",
    host="localhost",
    port="5432"
)

def get_next_id(cur, table, id_field):
    cur.execute(f"SELECT COALESCE(MAX({id_field}), 0) + 1 FROM {table};")
    return cur.fetchone()[0]

def insert_district(cur):
    district_id = get_next_id(cur, "district", "district_id")
    a2 = random.choice(["Almaty", "Astana", "Karaganda", "Shymkent", "Pavlodar"])
    a3 = random.choice(["Center", "North", "South", "East", "West"])
    nums = [random.randint(1000, 100000) for _ in range(10)]
    decimals = [round(random.uniform(0, 100), 2) for _ in range(3)]
    cur.execute("""
        INSERT INTO district (district_id, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (district_id, a2, a3, *nums[:6], decimals[0], nums[6], decimals[1], decimals[2], nums[7], nums[8], nums[9]))
    return district_id

def insert_client(cur, district_id):
    client_id = get_next_id(cur, "client", "client_id")
    gender = random.choice(["M", "F"])
    birth = date(1970, 1, 1) + timedelta(days=random.randint(5000, 18000))
    cur.execute("""
        INSERT INTO client (client_id, gender, birth_date, district_id)
        VALUES (%s, %s, %s, %s)
    """, (client_id, gender, birth, district_id))
    return client_id

def insert_account(cur, district_id):
    account_id = get_next_id(cur, "account", "account_id")
    frequency = random.choice(["MONTHLY", "WEEKLY", "AFTER_TRANSACTION"])
    created = datetime.now().date() - timedelta(days=random.randint(0, 1000))
    cur.execute("""
        INSERT INTO account (account_id, district_id, frequency, date)
        VALUES (%s, %s, %s, %s)
    """, (account_id, district_id, frequency, created))
    return account_id

def insert_disp(cur, client_id, account_id):
    disp_id = get_next_id(cur, "disp", "disp_id")
    type_ = random.choice(["OWNER", "DISPONENT"])
    cur.execute("""
        INSERT INTO disp (disp_id, client_id, account_id, type)
        VALUES (%s, %s, %s, %s)
    """, (disp_id, client_id, account_id, type_))
    return disp_id

def insert_card(cur, disp_id):
    card_id = get_next_id(cur, "card", "card_id")
    type_ = random.choice(["VISA", "MASTERCARD"])
    issued = datetime.now().date()
    cur.execute("""
        INSERT INTO card (card_id, disp_id, type, issued)
        VALUES (%s, %s, %s, %s)
    """, (card_id, disp_id, type_, issued))
    return card_id

def insert_loan(cur, account_id):
    loan_id = get_next_id(cur, "loan", "loan_id")
    amount = random.randint(1000, 50000)
    duration = random.choice([12, 24, 36, 48])
    payments = round(Decimal(amount / duration), 2)
    status = random.choice(["A", "B", "C", "D"])
    cur.execute("""
        INSERT INTO loan (loan_id, account_id, date, amount, duration, payments, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (loan_id, account_id, datetime.now().date(), amount, duration, payments, status))
    return loan_id

def insert_order(cur, account_id):
    order_id = get_next_id(cur, '"order"', "order_id")
    bank_to = random.choice(["KZ123", "KZ456", "KZ789"])
    account_to = random.randint(10000000, 99999999)
    amount = round(Decimal(random.uniform(100, 10000)), 2)
    k_symbol = random.choice(["UVER", "SIPO", "LEASING", "POJISTNE", None])
    cur.execute("""
        INSERT INTO "order" (order_id, account_id, bank_to, account_to, amount, k_symbol)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (order_id, account_id, bank_to, account_to, amount, k_symbol))
    return order_id

def insert_trans(cur, account_id):
    trans_id = get_next_id(cur, "trans", "trans_id")
    types = ["PRIJEM", "VYDAJ"]
    operations = ["CASH", "WITHDRAW", "REMITTANCE", "CREDIT"]
    k_symbols = ["UVER", "SIPO", "LEASING", "POJISTNE", None]
    banks = ["Komerční banka", "ČSOB", "Raiffeisen", "Moneta"]

    type_ = random.choice(types)
    operation = random.choice(operations)
    amount = random.randint(100, 10000)
    balance = random.randint(0, 200000)
    k_symbol = random.choice(k_symbols)
    bank = random.choice(banks)
    account_to = random.randint(10000000, 99999999)

    cur.execute("""
        INSERT INTO trans (trans_id, account_id, date, type, operation, amount, balance, k_symbol, bank, account)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (trans_id, account_id, datetime.now().date(), type_, operation, amount, balance, k_symbol, bank, account_to))
    return trans_id


while True:
    with conn.cursor() as cur:
        district_id = insert_district(cur)
        client_id = insert_client(cur, district_id)
        account_id = insert_account(cur, district_id)
        disp_id = insert_disp(cur, client_id, account_id)
        insert_card(cur, disp_id)
        insert_loan(cur, account_id)
        insert_order(cur, account_id)
        insert_trans(cur, account_id)
        conn.commit()

        print(f"Добавлена новая запись (account_id={account_id}, client_id={client_id})")

    time.sleep(10)
