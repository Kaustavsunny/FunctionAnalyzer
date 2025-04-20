import streamlit as st
import pandas as pd
import bcrypt
import os

# Set page config first
st.set_page_config(page_title="Function Analyzer", layout="wide")

# Constants
USER_DB = "users.csv"

# Initialize user database if not exists
if not os.path.exists(USER_DB):
    df = pd.DataFrame(columns=["username", "password", "approved"])
    df.to_csv(USER_DB, index=False, encoding="utf-8")

# ===== Helper Functions =====
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def get_users():
    return pd.read_csv(USER_DB, encoding="utf-8")

def save_user(username, password):
    df = get_users()
    if username in df["username"].values:
        return False
    hashed_pw = hash_password(password)
    new_user = pd.DataFrame([{
        "username": username,
        "password": hashed_pw,
        "approved": False
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_DB, index=False, encoding="utf-8")
    return True

def approve_user(username):
    df = get_users()
    df.loc[df["username"] == username, "approved"] = True
    df.to_csv(USER_DB, index=False, encoding="utf-8")

def authenticate_user(username, password):
    df = get_users()
    user = df[df["username"] == username]
    if not user.empty and check_password(password, user.iloc[0]["password"]):
        if user.iloc[0]["approved"]:
            return True, "Login successful."
        else:
            return False, "Your account is pending admin approval."
    return False, "Invalid credentials."

# ===== Session Initialization =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ===== Logout Handler =====
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged out successfully.")
    st.experimental_rerun()

# ===== Admin Panel =====
def admin_panel():
    st.title("🛠️ Admin Panel")
    st.write("Approve new user accounts below:")
    df = get_users()
    pending = df[df["approved"] == False]
    if pending.empty:
        st.success("No pending users.")
    for idx, row in pending.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"🔸 `{row['username']}`")
        with col2:
            if st.button(f"Approve {row['username']}", key=f"approve_{idx}"):
                approve_user(row["username"])
                st.success(f"{row['username']} approved!")
                st.experimental_rerun()
    st.markdown("---")
    if st.button("🚪 Logout"):
        logout()

# ===== Login and Signup Page =====
def login_page():
    st.title("🔐 Login / Signup")

    menu = ["Login", "Signup"]
    choice = st.radio("Choose an option", menu)

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = authenticate_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(msg)
                st.experimental_rerun()
            else:
                st.error(msg)

    elif choice == "Signup":
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        if st.button("Signup"):
            if save_user(username, password):
                st.success("✅ Signup successful! Awaiting admin approval.")
            else:
                st.warning("⚠️ Username already exists. Try another.")

# ===== Main App Loader =====
def load_function_analyzer():
    st.success(f"Welcome, `{st.session_state.username}`! 🎉")
    if st.button("🚪 Logout"):
        logout()
    st.markdown("---")
    try:
        with open("function_analyzer.py", "r", encoding="utf-8") as f:
            code = f.read()
            exec(code, globals())
    except Exception as e:
        st.error(f"Error loading function analyzer: {e}")

# ===== App Routing =====
if st.session_state.username == "admin":
    admin_panel()
elif not st.session_state.logged_in:
    login_page()
else:
    load_function_analyzer()
