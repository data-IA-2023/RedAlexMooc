import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import re
from Sentiment_analysis import translate_and_analyse_sentiment
from dotenv import load_dotenv
import os

load_dotenv()

MONGOURL   = os.environ.get('MONGOURL')
# MongoDB connection
client = MongoClient(MONGOURL)
db = client['RemiGOAT']
users_collection = db['UserData']

def create_user(username, email, gender, city, country, year_of_birth, level_of_education, csp):
    users_collection.insert_one({
        'username': username,
        'email': email,
        'gender': gender,
        'city': city,
        'country': country,
        'year_of_birth': year_of_birth,
        'level_of_education': level_of_education,
        'csp': csp
    })

def authenticate(username, email):
    user = users_collection.find_one({'username': username, 'email': email})
    return user is not None

def validate_email(email):
    # Basic regex for validating an email address
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_username(username):
    # Example check for username validity: not empty and no special characters
    return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

def validate_year_of_birth(year_of_birth):
    # Check if the year of birth is a valid year and not in the future
    try:
        year = int(year_of_birth)
        current_year = datetime.now().year
        return 1900 <= year <= current_year
    except ValueError:
        return False

# Manage session state for page navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'Login'

# Login page
def login_page():
    st.title("Login")
    input_email = st.text_input("Email")
    input_username = st.text_input("Username")

    if st.button("Login"):
        if authenticate(input_username, input_email):
            st.session_state['session_username'] = input_username
            st.session_state['page'] = 'Message'
            st.experimental_rerun()
        else:
            st.error('Email or username is incorrect')

# Account creation page
def create_account_page():
    st.title("Create Account")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email")
    new_gender = st.text_input("Gender")
    new_city = st.text_input("City")
    new_country = st.text_input("Country")
    new_year_of_birth = st.text_input("Year of Birth")
    new_level_of_education = st.text_input("Level of Education")
    new_csp = st.text_input("CSP")

    if st.button("Create Account"):
        # Validation checks
        if not validate_username(new_username):
            st.error("Invalid username. Only letters, numbers, and underscores are allowed.")
        elif not validate_email(new_email):
            st.error("Invalid email address.")
        elif not validate_year_of_birth(new_year_of_birth):
            st.error("Invalid year of birth. Please enter a valid year.")
        elif not new_gender or not new_city or not new_country or not new_level_of_education or not new_csp:
            st.error("All fields must be filled.")
        elif users_collection.find_one({'username': new_username}) or users_collection.find_one({'email': new_email}):
            st.error("Username or Email already exists")
        else:
            create_user(new_username, new_email, new_gender, new_city, new_country, new_year_of_birth, new_level_of_education, new_csp)
            st.success("Account created successfully! You can now log in.")
            st.session_state['page'] = 'Login'
            st.experimental_rerun()

# Message page
def message_page():
    st.title("Sentiment Analysis")
    message = st.text_area("Enter your message...")

    if st.button("Analyze"):
        if message:
            emotion_labels = translate_and_analyse_sentiment(message)
            st.write(emotion_labels)
        else:
            st.error("Please enter a message to analyze.")

# Sidebar for navigation
st.sidebar.title("Navigation")
if 'session_username' in st.session_state:
    st.sidebar.write(f"Logged in as {st.session_state['session_username']}")
    if st.sidebar.button("Logout"):
        del st.session_state['session_username']
        st.session_state['page'] = 'Login'
        st.experimental_rerun()
else:
    st.sidebar.write("Not logged in")
    choice = st.sidebar.selectbox("Choose Action", ["Login", "Create Account"])
    if choice == "Login":
        st.session_state['page'] = 'Login'
    elif choice == "Create Account":
        st.session_state['page'] = 'Create Account'

# Display the appropriate page based on the session state
if st.session_state['page'] == 'Login':
    login_page()
elif st.session_state['page'] == 'Create Account':
    create_account_page()
elif st.session_state['page'] == 'Message':
    message_page()