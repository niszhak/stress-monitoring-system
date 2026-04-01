import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import random
import os

from database import *

# ---------------------------------------------------------
# SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="NIKA MindTech", layout="wide")

create_tables()
create_default_employee()
model = joblib.load("stress_model.pkl")

# ---------------------------------------------------------
# MODE DETECTION (IMPORTANT)
# ---------------------------------------------------------
HARDWARE_MODE = os.path.exists("live.txt")

# ---------------------------------------------------------
# HARDWARE FUNCTIONS
# ---------------------------------------------------------
def get_fingerprint():
    try:
        with open("fingerprint.txt", "r") as f:
            return int(f.read())
    except:
        return None

def get_live_data():
    try:
        with open("live.txt", "r") as f:
            data = f.read().split(",")
            return int(data[1]), int(data[2]), float(data[3])
    except:
        return None, None, None

# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# =========================================================
# LOGIN PAGE
# =========================================================
if not st.session_state.login:

    st.title("NIKA MINDTECH")

    role = st.selectbox("Login As", ["Employee", "Manager"])

    user_id = st.text_input("ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if role == "Employee":
            if validate_employee(user_id, password):
                st.session_state.login = True
                st.session_state.role = role
                st.session_state.user = user_id
                st.rerun()
            else:
                st.error("Invalid Employee Login")

        else:
            if user_id == "admin" and password == "admin123":
                st.session_state.login = True
                st.session_state.role = role
                st.session_state.user = user_id
                st.rerun()
            else:
                st.error("Invalid Manager Login")

    # 🔒 FINGERPRINT LOGIN (AUTO SWITCH)
    if st.button("🔒 Fingerprint Login"):

        if HARDWARE_MODE:
            fid = get_fingerprint()
        else:
            fid = "FP001"   # Demo mode

        if fid:
            emp = get_employee_by_fingerprint(fid)

            if emp:
                st.session_state.login = True
                st.session_state.role = "Employee"
                st.session_state.user = emp[0]
                st.success(f"Logged in via fingerprint: {emp[1]}")
                st.rerun()
            else:
                st.error("Fingerprint not registered")
        else:
            st.error("No fingerprint detected")

# =========================================================
# MAIN APP
# =========================================================
else:

    role = st.session_state.role
    user = st.session_state.user

    st.sidebar.title("NIKA")

    def nav(x):
        if st.sidebar.button(x):
            st.session_state.menu = x

    if role == "Employee":
        nav("Dashboard")
        nav("Stress Monitoring")
        nav("Wellness")
    else:
        nav("Manager Dashboard")
        nav("Register Employee")

    menu = st.session_state.menu

# =========================================================
# REGISTER EMPLOYEE
# =========================================================
    if menu == "Register Employee":

        st.title("Register Employee")

        name = st.text_input("Name")
        dept = st.text_input("Department")

        fid = None

        # 🔍 SCAN FINGERPRINT
        if st.button("Scan Fingerprint"):
            if HARDWARE_MODE:
                fid = get_fingerprint()
            else:
                fid = "FP" + str(random.randint(100,999))

            if fid:
                st.success(f"Fingerprint Captured! ID: {fid}")
            else:
                st.error("Scan failed")

        # ✅ REGISTER
        if st.button("Register"):
            if fid:
                emp_id = generate_employee_id()
                pwd = generate_password()

                insert_employee(emp_id, name, dept, pwd, str(fid))

                st.success(f"""
                Employee Registered  
                ID: {emp_id}  
                Password: {pwd}  
                Fingerprint ID: {fid}
                """)
            else:
                st.error("Scan fingerprint first!")

# =========================================================
# DASHBOARD
# =========================================================
    if menu == "Dashboard":

        st.title("Dashboard")

        df = fetch_employee_data(user)

        st.metric("Records", len(df))

        if df:
            df = pd.DataFrame(df, columns=[
                "id","employee_id","heart_rate","hrv","temp",
                "workload","sleep","stress","timestamp"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.plotly_chart(px.line(df, x="timestamp", y="stress"))

# =========================================================
# STRESS MONITORING
# =========================================================
    if menu == "Stress Monitoring":

        st.title("Stress Monitoring")

        # 🔁 AUTO MODE SWITCH
        if HARDWARE_MODE:
            fid, hr, temp = get_live_data()
        else:
            fid = "FP001"
            hr = random.randint(65, 95)
            temp = round(random.uniform(36.0, 37.5), 2)

        if hr:
            st.write("Heart Rate:", hr)
            st.write("Temperature:", temp)

            emp = get_employee_by_fingerprint(fid)
            if emp:
                st.write("Employee:", emp[1])
        else:
            st.warning("Waiting for sensor data...")

        workload = st.slider("Workload",1,10)
        sleep = st.slider("Sleep",3.0,8.0)

        if st.button("Predict Stress"):

            if hr:
                df = pd.DataFrame([{
                    "heart_rate": hr,
                    "hrv": 50,
                    "temp": temp,
                    "workload": workload,
                    "sleep": sleep
                }])

                stress = int(model.predict(df)[0])

                insert_record(user, hr, 50, temp, workload, sleep, stress)

                st.success(f"Stress Level: {stress}")
            else:
                st.error("No sensor data")

# =========================================================
# WELLNESS
# =========================================================
    if menu == "Wellness":

        st.title("Wellness Q&A")

        qa = {
            "How to reduce stress?": "Deep breathing, rest, hydration, short breaks.",
            "Signs of stress?": "Headache, fatigue, poor sleep, irritability.",
            "Best sleep hours?": "7–8 hours recommended.",
            "Exercise benefit?": "Improves mood and reduces stress."
        }

        q = st.selectbox("Choose Question", list(qa.keys()))
        st.info(qa[q])

# =========================================================
# MANAGER DASHBOARD
# =========================================================
    if menu == "Manager Dashboard":

        st.title("Manager Dashboard")

        df = fetch_all_data()

        if df:
            df = pd.DataFrame(df, columns=[
                "id","employee_id","heart_rate","hrv","temp",
                "workload","sleep","stress","timestamp"
            ])
            st.plotly_chart(px.pie(df, names="stress"))
        else:
            st.info("No data available")

# =========================================================
# LOGOUT
# =========================================================
    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.rerun()
