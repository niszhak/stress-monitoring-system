import sqlite3
import random
import string
from datetime import datetime

DB_NAME = "nika.db"

# ---------------------------------------------------------
# CONNECTION
# ---------------------------------------------------------
def connect():
    return sqlite3.connect(DB_NAME)

# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------
def create_tables():
    conn = connect()
    c = conn.cursor()

    # Employees Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        name TEXT,
        department TEXT,
        password TEXT,
        fingerprint_id TEXT
    )
    """)

    # Stress Data Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS stress_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        heart_rate REAL,
        hrv REAL,
        temp REAL,
        workload INTEGER,
        sleep REAL,
        stress INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# DEFAULT EMPLOYEE + MANAGER
# ---------------------------------------------------------
def create_default_employee():
    conn = connect()
    c = conn.cursor()

    # Manager default
    c.execute("SELECT * FROM employees WHERE id='admin'")
    if not c.fetchone():
        c.execute("""
        INSERT INTO employees VALUES 
        ('admin','Manager','Admin','admin123','FP_ADMIN')
        """)

    # Test employee
    c.execute("SELECT * FROM employees WHERE id='EMP001'")
    if not c.fetchone():
        c.execute("""
        INSERT INTO employees VALUES 
        ('EMP001','John Doe','IT','1234','FP001')
        """)

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# EMPLOYEE FUNCTIONS
# ---------------------------------------------------------
def insert_employee(emp_id, name, dept, password, fingerprint_id):
    conn = connect()
    c = conn.cursor()

    # Ensure fingerprint is stored as string
    fingerprint_id = str(fingerprint_id)

    c.execute("INSERT INTO employees VALUES (?,?,?,?,?)",
              (emp_id, name, dept, password, fingerprint_id))

    conn.commit()
    conn.close()

def validate_employee(emp_id, password):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM employees WHERE id=? AND password=?",
              (emp_id, password))

    result = c.fetchone()
    conn.close()
    return result

# ---------------------------------------------------------
# FINGERPRINT FUNCTIONS
# ---------------------------------------------------------
def fingerprint_login(fingerprint_id):
    conn = connect()
    c = conn.cursor()

    fingerprint_id = str(fingerprint_id)

    c.execute("SELECT * FROM employees WHERE fingerprint_id=?",
              (fingerprint_id,))

    result = c.fetchone()
    conn.close()

    return result[0] if result else None

# ✅ MAIN FUNCTION USED IN APP
def get_employee_by_fingerprint(fid):
    conn = connect()
    c = conn.cursor()

    fid = str(fid)

    c.execute("SELECT id, name FROM employees WHERE fingerprint_id=?",
              (fid,))

    result = c.fetchone()
    conn.close()

    return result

# ---------------------------------------------------------
# STRESS DATA
# ---------------------------------------------------------
def insert_record(emp_id, hr, hrv, temp, workload, sleep, stress):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    INSERT INTO stress_data 
    (employee_id, heart_rate, hrv, temp, workload, sleep, stress, timestamp)
    VALUES (?,?,?,?,?,?,?,?)
    """, (emp_id, hr, hrv, temp, workload, sleep, stress, datetime.now()))

    conn.commit()
    conn.close()

def fetch_employee_data(emp_id):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM stress_data WHERE employee_id=?", (emp_id,))
    rows = c.fetchall()

    conn.close()
    return rows

def fetch_all_data():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM stress_data")
    rows = c.fetchall()

    conn.close()
    return rows

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------
def generate_employee_id():
    return "EMP" + str(random.randint(100,999))

def generate_password(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
