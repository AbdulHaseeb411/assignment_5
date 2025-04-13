import streamlit as st
import hashlib
import json
import time
import uuid
import base64
from cryptography.fernet import Fernet

# Title
st.title("🔐 Simple Secure Data App")

# Session state init
if "stored_data" not in st.session_state:
    st.session_state.stored_data = {}
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0
if "last_attempt_time" not in st.session_state:
    st.session_state.last_attempt_time = 0

# Passkey hashing
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Create encryption key
def generate_key(passkey):
    key = hashlib.sha256(passkey.encode()).digest()
    return base64.urlsafe_b64encode(key[:32])

# Encrypt
def encrypt_data(data, passkey):
    key = generate_key(passkey)
    return Fernet(key).encrypt(data.encode()).decode()

# Decrypt
def decrypt_data(encrypted, passkey):
    try:
        key = generate_key(passkey)
        return Fernet(key).decrypt(encrypted.encode()).decode()
    except:
        return None

# Navigation
page = st.sidebar.selectbox("📍 Go to", ["Home", "Store Data", "Retrieve Data", "Login"])

# Lockout check
if st.session_state.failed_attempts >= 3:
    page = "Login"
    st.warning("Too many failed attempts. Please login to continue.")

# Store Page
if page == "Store Data":
    st.subheader("📝 Store Your Data")
    text = st.text_area("Enter Data")
    passkey = st.text_input("Passkey", type="password")
    confirm = st.text_input("Confirm Passkey", type="password")

    if st.button("Encrypt & Save"):
        if not text or not passkey or not confirm:
            st.error("Please fill all fields.")
        elif passkey != confirm:
            st.error("Passkeys do not match.")
        else:
            data_id = str(uuid.uuid4())
            encrypted = encrypt_data(text, passkey)
            st.session_state.stored_data[data_id] = {
                "encrypted": encrypted,
                "passkey": hash_passkey(passkey)
            }
            st.success("Data saved successfully!")
            st.info("Save your Data ID to retrieve later:")
            st.code(data_id, language="text")

# Retrieve Page
elif page == "Retrieve Data":
    st.subheader("📂 Retrieve Your Data")
    data_id = st.text_input("Enter Data ID")
    passkey = st.text_input("Enter Passkey", type="password")

    if st.button("Decrypt"):
        if not data_id or not passkey:
            st.error("All fields are required.")
        elif data_id in st.session_state.stored_data:
            encrypted = st.session_state.stored_data[data_id]["encrypted"]
            decrypted = decrypt_data(encrypted, passkey)

            if decrypted:
                st.success("Data Decrypted Successfully!")
                st.code(decrypted, language="text")
                st.session_state.failed_attempts = 0
            else:
                st.session_state.failed_attempts += 1
                st.error(f"Wrong passkey! Attempts left: {3 - st.session_state.failed_attempts}")
        else:
            st.error("Data ID not found.")

# Login Page
elif page == "Login":
    st.subheader("🔒 Admin Login")
    if time.time() - st.session_state.last_attempt_time < 10:
        wait_time = int(10 - (time.time() - st.session_state.last_attempt_time))
        st.warning(f"Please wait {wait_time} seconds before retry.")
    else:
        admin_pass = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if admin_pass == "admin123":
                st.success("Logged in successfully.")
                st.session_state.failed_attempts = 0
            else:
                st.session_state.last_attempt_time = time.time()
                st.error("Incorrect admin password.")

# Home Page
else:
    st.subheader("🏠 Welcome!")
    st.write("Use this app to securely store and retrieve data using your own passkey.")
    st.info(f"🔐 Stored Entries: {len(st.session_state.stored_data)}")
    st.markdown("👨‍💻 Created with ❤️ by **Abdul Haseeb**")
