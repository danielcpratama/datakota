import streamlit as st
from google.cloud import storage
import bcrypt
import datetime
import time
from st_files_connection import FilesConnection
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from selenium import webdriver


gcs_credentials = st.secrets.connections.gcs
storage_client = storage.Client.from_service_account_info(info=gcs_credentials)
bucket = storage_client.get_bucket('datakota-bucket')



def store_user_data(username, hashed_password, email, phone, role, sector, company, NIM, source):
    """Store user data in Google Cloud Storage"""
    # Check if username already exists
    if username_exists(username):
        st.error("Username already exists. Please choose a different one.")
        return False
    
    # Construct data to store
    user_data = {
        "username": username,
        "hashed_password": hashed_password,
        "email": email,
        "phone" : phone,
        "role": role,
        "sector" : sector,
        "company" : company,
        "NIM": NIM,
        "source": source,
        
    }
    
    # Store data in GCS
    blob = bucket.blob(f"users/{username}.json")
    blob.upload_from_string(str(user_data))
    return True

def username_exists(username):
    """Check if username already exists in Google Cloud Storage"""
    blob = bucket.blob(f"users/{username}.json")
    return blob.exists()

def verify_password(username, password):
    """Verify user's password"""
    blob = bucket.blob(f"users/{username}.json")
    if blob.exists():
        user_data = eval(blob.download_as_string())
        stored_hashed_password = user_data["hashed_password"]
        return bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password)
    return False

def is_pass_inactive(username):
    """Check if the user has an active pass"""
    blob = bucket.blob(f"users/{username}.json")
    if blob.exists():
        user_data = eval(blob.download_as_string())
        if "end_time" in user_data:
            end_time = user_data["end_time"]
            if end_time < (datetime.datetime.now() + datetime.timedelta(hours=7)):
                st.session_state["end"] = end_time
                # st.session_state['payment'] = user_data["payment"]
                return True
            else:
                return False


def log_login(username):
    """log session to google sheets for tracking"""
    conn_gsheets = st.connection("gsheets", type=GSheetsConnection)
    existing_data = conn_gsheets.read(worksheet='signin', usecols = list(range(7)),ttl=5)
    blob = bucket.blob(f"users/{username}.json")
    if blob.exists():
        user_data = eval(blob.download_as_string())
        st.session_state["role"] = user_data["role"]
    updated_data = pd.DataFrame([{
                        "timestamp" : (datetime.datetime.now()+ datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                        "username" : st.session_state['username'],
                        "role" : st.session_state["role"],
                        "payment" : st.session_state['payment'],
                        "start" : st.session_state['start'],
                        "end" : st.session_state['end']
                            
                            }])
    updated_df = pd.concat([existing_data, updated_data])
    conn_gsheets.update(worksheet='signin', data=updated_df)


# ------SIGN IN NEW----------------------------------------------------------------------------------------------------------------

def sign_in():
    # Initialize session state
    if "username" not in st.session_state:
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["payment"] = ""
        st.session_state["start"] = ""
        st.session_state["end"] = ""
        st.session_state["disabled_status"] = ""

    # Check if user is sign in
    if st.session_state["username"]:
        st.info(f"You are already signed in as {st.session_state['username']}.")
        st.info(f"Your pass will be expired on {st.session_state['end']}.")
        st.session_state["disabled_status"] = False
    else:
        # get username & password
        with st.container(border=True):
            st.session_state["disabled_status"] = True
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            # Is pass active?
            if is_pass_inactive(username) == False:
                st.info("You have an active pass. No payment required.")
                if st.button('sign in with your active pass', key='active_signin'):
                    if verify_password(username, password):
                        # Update session state
                        blob = bucket.blob(f"users/{username}.json")
                        if blob.exists():
                            user_data = eval(blob.download_as_string())
                            st.session_state["username"] = user_data['username']
                            st.session_state["role"] = user_data['role']
                            st.session_state["start"] = user_data['start_time']
                            st.session_state["end"] = user_data['end_time']
                            st.session_state["disabled_status"] = False
                            
                        # Log Login
                        log_login(username)
                        # success
                        st.success("Sign in successful!")
                    else: 
                        st.error("Invalid username or password.")
            else: 
                # check username if entitled to a free pass
                
                blob = bucket.blob(f"users/{username}.json")
                if blob.exists():
                    user_data = eval(blob.download_as_string())
                    st.session_state["role"] = user_data["role"]
                    
                    # if username entitled to a free pass:
                    
                    if st.session_state["role"] in ["Student", "Educator", "Researcher", "NGO/Non-Profit Worker"]:
                        st.info("You have exclusive free access!")
                        st.session_state["payment"] = "Free"
                        if st.button('sign in with your free pass', key='free_signin'):
                            if verify_password(username, password):
                                # Update session state
                                blob = bucket.blob(f"users/{username}.json")
                                if blob.exists():
                                    user_data = eval(blob.download_as_string())
                                    st.session_state["username"] = user_data['username']
                                    st.session_state["role"] = user_data['role']
                                    st.session_state["disabled_status"] = False
                                # Log Login
                                log_login(username)
                                # success
                                st.success("Sign in successful!")
                            else: 
                                st.error("Invalid username or password.")
                    
                    # if username is not entitled to a free pass:
                    else:
                        st.info("You don't have an active pass. Please buy a pass")
                        st.session_state["payment"] = st.selectbox("Choose your pass*", ["Daily pass @IDR 15.000", "Weekly pass @IDR 50.000"], placeholder="Pick one")
                        st.write(f'scan QRIS and pay {st.session_state["payment"]}')
                        st.image('logo/QRIS_small.jpg', width=200)
                        st.text_input('last four digits of your QRIS payment reference number', max_chars=4)
                        if st.button('submit payment & sign in', key='paid_signin'):
                            if verify_password(username, password):
                                # Update session state
                                current_time = datetime.datetime.now() + datetime.timedelta(hours=7)
                                start_time = current_time
                                end_time = (current_time + datetime.timedelta(days=1)) if st.session_state["payment"] == "Daily pass @IDR 15.000" else (current_time + datetime.timedelta(days=7))
                                blob = bucket.blob(f"users/{username}.json")
                                if blob.exists():
                                    user_data = eval(blob.download_as_string())
                                    user_data["start_time"] = start_time
                                    user_data["end_time"] = end_time
                                    blob.upload_from_string(str(user_data))
                                    st.session_state["username"] = user_data['username']
                                    st.session_state["role"] = user_data['role']
                                    st.session_state["start"] = user_data['start_time']
                                    st.session_state["end"] = user_data['end_time']
                                    st.session_state["disabled_status"] = False
                                
                                # Log Login
                                log_login(username)
                                # success
                                with st.spinner('confirming your payment'):
                                    time.sleep(5)
                                    st.success(f"Your {st.session_state['payment']} has been activated.")
                            else: 
                                st.error("Invalid username or password.")
            

# ----------------------------------------------------------------------------------------------------------------------                      

# Function to capture screenshot of Folium map
def save_map(html_file, output_file):
    browser = webdriver.Chrome()
    browser.set_window_size(800, 600)  # Set the window size according to your requirement
    browser.get(html_file)
    time.sleep(5)  # Give some time for the map to render
    browser.save_screenshot(output_file)
    browser.quit()



# ----------------------------------------------------------------------------------------------------------------------
# SIGN UP
def sign_up():
    with st.container(border=True):
        username = st.text_input("Username*")
        password = st.text_input("Password*", type="password")
        email = st.text_input("Email*")
        phone = st.text_input("phone number*")
        role = st.selectbox("Tell us about your role*", ["Student", "Educator", "Researcher", "NGO/Non-Profit Worker", "Consultant", "Private Employee", "Civil Servant", "Enterpreneurs", "Others"], placeholder="Pick one", index=None)
        sector = st.multiselect("Which sector do you work on?*", 
                                [   "Urban Planning",
                                    "Real Estate",
                                    "Business/Startup",
                                    "Healthcare Services",
                                    "Environmental Conservation",
                                    "Transportation Logistics",
                                    "Retail/FnB",
                                    "Disaster Management",
                                    "Social Services",
                                    "Tourism & Hospitality",
                                    "Agriculture",
                                    "Energy",
                                    "Insurance Risk",
                                    "Telecommunications",
                                    "Water",
                                    "Other"], placeholder="Choose one or more")
        company = st.text_input("Name of your company/school/university*")
        NIM = st.text_input("Nomor Induk Mahasiswa/Dosen Nasional")
        source = st.multiselect("How did you hear about our platform?*", ["twitter", "instagram", "whatsApp", "friends"], placeholder="Choose one or more")
    
    # Check if all fields are filled
    if not (username and password and email and phone and role and sector and company and source):
        st.error("Please fill out all required fields marked with *")
    
    # Check if username already exists
    elif username_exists(username):
        st.error("Username already exists. Please choose a different one.")

    else:
        colA, colB = st.columns([1,1])
        with colB:
            if st.button("Sign me up!", use_container_width=True, type='primary'):
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                if store_user_data(username, hashed_password, email, phone, role, sector, company, NIM, source):
                    st.success("Sign up successful! Please proceed to sign in.")
