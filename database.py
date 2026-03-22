import sqlite3
import random

DB = "stress.db"

# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------
def create_tables():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS employees(
        emp_id TEXT PRIMARY KEY,
        name TEXT,
        dept TEXT,
        password TEXT,
        fingerprint TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS stress(
        emp_id TEXT,
        heart_rate INT,
        hrv INT,
        temp REAL,
        workload INT,
        sleep REAL,
        stress INT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# DEFAULT EMPLOYEE
# ---------------------------------------------------------
def create_default_employee():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM employees WHERE emp_id='E101'")
    user = c.fetchone()

    if not user:
        c.execute("""
            INSERT INTO employees VALUES(?,?,?,?,?)
        """, ("E101","Test User","Demo","123","FP101"))

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# GENERATORS
# ---------------------------------------------------------
def generate_employee_id():
    return "E" + str(random.randint(100,999))

def generate_password():
    return str(random.randint(100,999))

# ---------------------------------------------------------
# INSERT
# ---------------------------------------------------------
def insert_employee(emp_id,name,dept,password,fingerprint):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO employees VALUES(?,?,?,?,?)",
              (emp_id,name,dept,password,fingerprint))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
def validate_employee(emp_id,password):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE emp_id=? AND password=?",
              (emp_id,password))
    result = c.fetchone()
    conn.close()
    return result

# Fingerprint simulation
def fingerprint_login():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT emp_id FROM employees ORDER BY RANDOM() LIMIT 1")
    result = c.fetchone()

    conn.close()

    return result[0] if result else None

# ---------------------------------------------------------
# DATA
# ---------------------------------------------------------
def insert_record(emp,hr,hrv,temp,work,sleep,stress):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO stress VALUES(?,?,?,?,?,?,?,datetime('now'))",
              (emp,hr,hrv,temp,work,sleep,stress))
    conn.commit()
    conn.close()

def fetch_all_data():
    conn = sqlite3.connect(DB)
    import pandas as pd
    df = pd.read_sql("SELECT * FROM stress", conn)
    conn.close()
    return df

def fetch_employee_data(emp):
    conn = sqlite3.connect(DB)
    import pandas as pd
    df = pd.read_sql("SELECT * FROM stress WHERE emp_id=?", conn, params=(emp,))
    conn.close()
    return df
