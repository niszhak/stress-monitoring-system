# =========================================================
# NIKA MINDTECH - FINAL COMPLETE SYSTEM (WITH SENSOR SUPPORT)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import random
import serial  # for hardware integration (optional)

from database import *

# ---------------------------------------------------------
# SETTINGS
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
# INIT
# ---------------------------------------------------------
create_tables()
create_default_employee()
model = joblib.load("stress_model.pkl")

# ---------------------------------------------------------
# SENSOR FUNCTION (PLACEHOLDER / READY FOR HARDWARE)
# ---------------------------------------------------------
def get_sensor_data():
    """
    Replace this with real Arduino/serial data later.
    For now returns simulated values.
    """

    try:
        # Example serial reading (UNCOMMENT when hardware ready)
        # ser = serial.Serial('COM3', 9600, timeout=1)
        # line = ser.readline().decode().strip()
        # values = line.split(',')
        # return {
        #     "heart_rate": float(values[0]),
        #     "hrv": float(values[1]),
        #     "temp": float(values[2])
        # }

        # Temporary simulated data
        return {
            "heart_rate": random.randint(65, 95),
            "hrv": random.randint(40, 80),
            "temp": round(random.uniform(36.0, 37.5), 2)
        }

    except:
        return {
            "heart_rate": 70,
            "hrv": 60,
            "temp": 36.5
        }

# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# =========================================================
# LOGIN
# =========================================================
if not st.session_state.login:

    st.title("NIKA MINDTECH")

    role = st.selectbox("Login As", ["Employee","Manager"])
    user_label = "Employee ID" if role=="Employee" else "Manager ID"

    user_id = st.text_input(user_label)
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if role == "Employee":
            if validate_employee(user_id, password):
                st.session_state.login=True
                st.session_state.role=role
                st.session_state.user=user_id
                st.rerun()
            else:
                st.error("Invalid Employee Login")

        else:
            if user_id=="admin" and password=="admin":
                st.session_state.login=True
                st.session_state.role=role
                st.session_state.user=user_id
                st.rerun()
            else:
                st.error("Invalid Manager Login")

    # Fingerprint login (placeholder)
    if st.button("🔒 Fingerprint Login"):
        emp = fingerprint_login()
        if emp:
            st.session_state.login=True
            st.session_state.role="Employee"
            st.session_state.user=emp
            st.success(f"Logged in as {emp}")
            st.rerun()

# =========================================================
# MAIN APP
# =========================================================
else:

    role = st.session_state.role
    user = st.session_state.user

    st.sidebar.title("🧠 NIKA")

    def nav(x):
        if st.sidebar.button(x):
            st.session_state.menu=x

    if role=="Employee":
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
    if menu=="Register Employee":

        st.title("Register Employee")

        name = st.text_input("Name")
        dept = st.text_input("Department")

        fingerprint=None
        if st.button("Scan Fingerprint"):
            fingerprint=f"FP{random.randint(100,999)}"
            st.success(f"Captured: {fingerprint}")

        if st.button("Register"):
            emp_id=generate_employee_id()
            pwd=generate_password()
            insert_employee(emp_id,name,dept,pwd,fingerprint)
            st.success(f"ID: {emp_id} | Password: {pwd}")

# =========================================================
# DASHBOARD
# =========================================================
    if menu=="Dashboard":

        st.title("Dashboard")

        df=fetch_employee_data(user)
        st.metric("Records",len(df))

        if not df.empty:
            df["timestamp"]=pd.to_datetime(df["timestamp"])
            st.plotly_chart(px.line(df,x="timestamp",y="stress"))

# =========================================================
# STRESS MONITORING (WITH SENSOR DATA)
# =========================================================
    if menu=="Stress Monitoring":

        st.title("Stress Monitoring (Live Sensor Data)")

        # ✅ GET DATA FROM SENSOR
        data = get_sensor_data()

        heart_rate = data["heart_rate"]
        hrv = data["hrv"]
        temp = data["temp"]

        st.write("Heart Rate:", heart_rate)
        st.write("HRV:", hrv)
        st.write("Temperature:", temp)

        workload = st.slider("Workload",1,10)
        sleep = st.slider("Sleep Hours",3.0,8.0)

        if st.button("Predict"):

            df=pd.DataFrame([{
                "heart_rate":heart_rate,
                "hrv":hrv,
                "temp":temp,
                "workload":workload,
                "sleep":sleep
            }])

            stress=int(model.predict(df)[0])
            insert_record(user,heart_rate,hrv,temp,workload,sleep,stress)

            st.success(f"Stress Level: {stress}")

# =========================================================
# WELLNESS
# =========================================================
    if menu=="Wellness":

        st.title("🧘 Wellness Q&A")

        questions = {
            "How to reduce stress quickly?":
                "Take deep breaths, pause work, drink water, and relax your body.",

            "What are signs of high stress?":
                "Headache, fatigue, irritation, poor sleep, and lack of focus.",

            "How much sleep is recommended?":
                "7–8 hours of quality sleep is ideal for adults.",

            "Best way to relax during work?":
                "Take a 5–10 minute break, stretch, or go for a short walk.",

            "How to improve mental health daily?":
                "Exercise, eat healthy, stay connected, and practice mindfulness.",

            "What to do when feeling overwhelmed?":
                "Break tasks into small steps and focus on one at a time.",

            "Does exercise reduce stress?":
                "Yes, it releases endorphins which improve mood and reduce stress."
        }

        selected_q = st.selectbox("Choose your question:", list(questions.keys()))

        if selected_q:
            st.markdown(f"<div class='qa-box'><b>Answer:</b><br>{questions[selected_q]}</div>", unsafe_allow_html=True)

# =========================================================
# MANAGER DASHBOARD
# =========================================================
    if menu=="Manager Dashboard":

        st.title("Manager Dashboard")

        df=fetch_all_data()
        st.plotly_chart(px.pie(df,names="stress"))

# =========================================================
# LOGOUT
# =========================================================
    if st.sidebar.button("Logout"):
        st.session_state.login=False
        st.rerun()
