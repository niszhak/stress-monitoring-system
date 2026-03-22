# =========================================================
# NIKA MINDTECH - FINAL SYSTEM (DEPLOYMENT SAFE)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import random

from database import *

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="NIKA MindTech", layout="wide")

# ---------------------------------------------------------
# UI STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#eef2ff,#e0f2fe);
}
[data-testid="stSidebar"] {
    background:#f8fafc;
}
.stButton>button {
    width:100%;
    border-radius:10px;
}
.qa-box {
    background:#f1f5f9;
    padding:15px;
    border-radius:10px;
    margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE + MODEL
# ---------------------------------------------------------
create_tables()
create_default_employee()
model = joblib.load("stress_model.pkl")

# ---------------------------------------------------------
# SENSOR DATA FUNCTION (HARDWARE READY STRUCTURE)
# ---------------------------------------------------------
def get_sensor_data():
    """
    HARDWARE INTEGRATION POINT

    For now → simulated values (so app works on Streamlit Cloud)

    Later → replace this with:
    - API call
    - Database fetch
    - Local bridge script (Arduino → Python → DB)
    """

    return {
        "heart_rate": random.randint(65, 95),
        "hrv": random.randint(40, 80),
        "temp": round(random.uniform(36.0, 37.5), 2)
    }

# ---------------------------------------------------------
# SESSION STATE
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
            if user_id == "admin" and password == "admin":
                st.session_state.login = True
                st.session_state.role = role
                st.session_state.user = user_id
                st.rerun()
            else:
                st.error("Invalid Manager Login")

# =========================================================
# MAIN APP
# =========================================================
else:

    role = st.session_state.role
    user = st.session_state.user

    st.sidebar.title("🧠 NIKA")

    def nav(page):
        if st.sidebar.button(page):
            st.session_state.menu = page

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

        fingerprint = None
        if st.button("Scan Fingerprint"):
            fingerprint = f"FP{random.randint(100,999)}"
            st.success(f"Captured: {fingerprint}")

        if st.button("Register"):
            emp_id = generate_employee_id()
            pwd = generate_password()
            insert_employee(emp_id, name, dept, pwd, fingerprint)
            st.success(f"ID: {emp_id} | Password: {pwd}")

# =========================================================
# DASHBOARD
# =========================================================
    if menu == "Dashboard":

        st.title("Dashboard")

        df = fetch_employee_data(user)
        st.metric("Records", len(df))

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            st.plotly_chart(px.line(df, x="timestamp", y="stress"))

# =========================================================
# STRESS MONITORING (WITH SENSOR DATA)
# =========================================================
    if menu == "Stress Monitoring":

        st.title("Stress Monitoring (Sensor Ready)")

        # ✅ GET SENSOR DATA
        data = get_sensor_data()

        heart_rate = data["heart_rate"]
        hrv = data["hrv"]
        temp = data["temp"]

        st.write("Heart Rate:", heart_rate)
        st.write("HRV:", hrv)
        st.write("Temperature:", temp)

        workload = st.slider("Workload", 1, 10)
        sleep = st.slider("Sleep Hours", 3.0, 8.0)

        if st.button("Predict Stress"):

            df = pd.DataFrame([{
                "heart_rate": heart_rate,
                "hrv": hrv,
                "temp": temp,
                "workload": workload,
                "sleep": sleep
            }])

            stress = int(model.predict(df)[0])

            insert_record(user, heart_rate, hrv, temp, workload, sleep, stress)

            st.success(f"Stress Level: {stress}")

# =========================================================
# WELLNESS MODULE (Q&A)
# =========================================================
    if menu == "Wellness":

        st.title("🧘 Wellness Q&A")

        questions = {
            "How to reduce stress quickly?":
                "Take deep breaths, relax, drink water, and take short breaks.",

            "What are signs of stress?":
                "Headache, fatigue, irritability, poor sleep, lack of focus.",

            "How much sleep is needed?":
                "7–8 hours of quality sleep is recommended.",

            "Best way to relax?":
                "Walk, meditate, stretch, or listen to calming music.",

            "How to improve mental health?":
                "Exercise, good sleep, healthy diet, social interaction.",

            "What to do when overwhelmed?":
                "Break tasks into small steps and prioritize.",

            "Does exercise help stress?":
                "Yes, it releases endorphins that improve mood."
        }

        q = st.selectbox("Choose a question:", list(questions.keys()))

        st.markdown(f"""
        <div class="qa-box">
        <b>Answer:</b><br>{questions[q]}
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# MANAGER DASHBOARD
# =========================================================
    if menu == "Manager Dashboard":

        st.title("Manager Dashboard")

        df = fetch_all_data()

        if not df.empty:
            st.plotly_chart(px.pie(df, names="stress"))
        else:
            st.info("No data available")

# =========================================================
# LOGOUT
# =========================================================
    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.rerun()
