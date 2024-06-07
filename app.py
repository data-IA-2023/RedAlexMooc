<<<<<<< HEAD
# Import des bibliothèques nécessaires
import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import re
from Sentiment_analysis import translate_and_analyse_sentiment
from dotenv import load_dotenv
import os


#import custom page
from Sentiment_analysis import translate_and_analyse_sentiment
from getDf import *
from message_analysis import *
from model_predict_classifier import *
from model_predict_regressor import * 
# Charger les variables d'environnement à partir du fichier .env
load_dotenv()
mlflow.set_tracking_uri(os.environ.get('MLFLOW_URL'))
# Connexion à MongoDB
MONGOURL = os.environ.get('MONGO_URL')
client = MongoClient(MONGOURL)
db = client['RemiGOAT']
users_collection = db['UserData']

# Définition de la fonction pour créer un utilisateur dans la base de données
def create_user(username, email, gender, city, country, year_of_birth, level_of_education, csp):
    users_collection.insert_one({
        'username': username,
        'email': email,
        'gender': gender,
        'city': city,
        'country': country,
        'year_of_birth': int(year_of_birth),
        'level_of_education': level_of_education,
        'CSP': csp
    })

# Définition de la fonction pour authentifier un utilisateur
def authenticate(username, email):
    user = users_collection.find_one({'username': username, 'email': email})
    return user is not None

# Fonction pour valider une adresse e-mail
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Fonction pour valider un nom d'utilisateur
def validate_username(username):
    return bool(re.match(r"^[a-zA-Z0-9_]+$", username))

# Fonction pour valider l'année de naissance
def validate_year_of_birth(year_of_birth):
    try:
        year = int(year_of_birth)
        current_year = datetime.now().year
        return 1924 <= year <= current_year
    except ValueError:
        return False

# Fonction pour la page de login
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

# Fonction pour la page de création de compte
def create_account_page():
    df = get_the_df()
    # Récupérer les valeurs uniques pour chaque colonne
    gender_options = sorted(df['gender'].unique())
    city_options = sorted(df['city'].unique())
    country_options = sorted(df['country'].unique())
    year_of_birth_options = sorted(df['year_of_birth'].unique().astype(int))
    level_of_education_options = sorted(df['level_of_education'].unique())
    csp_options = sorted(df['CSP'].unique())

    st.title("Create Account")
    new_username = st.text_input("Username")
    new_email = st.text_input("Email")

    # Utiliser selectbox pour les autres champs
    new_gender = st.selectbox("Gender", gender_options)
    new_city = st.selectbox("City", city_options)
    new_country = st.selectbox("Country", country_options)
    new_year_of_birth = st.selectbox("Year of Birth", year_of_birth_options)
    new_level_of_education = st.selectbox("Level of Education", level_of_education_options)
    new_csp = st.selectbox("CSP", csp_options)

    if st.button("Create Account"):
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

# Fonction pour la page d'analyse de sentiment
def message_page():
    global tokenizer,model
    st.title("Message Analysis")
    message = st.text_area("Enter your message...")

    if st.button("Analyze"):
        emotion_labels = translate_and_analyse_sentiment(message)
        thread_analyse, message_analyse =faq(message, tokenizer, model)
        if message:
                # Initialisation de MLflow
            mlflow.set_experiment("Message_Analysis_Prediction")

            with mlflow.start_run(run_name=f"Message_analysis_run {datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
                
                # Enregistrement des paramètres et métriques dans MLflow
                mlflow.log_param("body", message)
                mlflow.log_param("thread", thread_analyse)
                mlflow.log_param("message similaire", message_analyse)
                mlflow.log_param("langue", emotion_labels['langue'])
                mlflow.log_param("traduction", emotion_labels['traduction'])
                mlflow.log_param("emotion", emotion_labels['emotion'])
                mlflow.log_param("sentiment", emotion_labels['sentiment'])
                mlflow.log_param("emoticon", emotion_labels['emoticon'])
                mlflow.log_param("emoticon", emotion_labels['emoticon'])
            st.write(f"Thread : {thread_analyse}")
            st.write(f"Message similaire : {message_analyse}")
            st.write(emotion_labels)
        else:
            st.error("Please enter a message to analyze.")

def certif_page():
    st.title(f"Does {st.session_state['session_username']} will get the certif")
    cours = ["04026", "04017", "04021", "04018"]
    selected_cours = st.selectbox("Cours", cours)
    
    user_data = users_collection.find_one({'username': st.session_state['session_username']})

    if user_data:
        user_predict = {
            'level_of_education': user_data['level_of_education'],  
            'CSP': user_data['CSP'],        
            'country': user_data['country'],          
            'gender': user_data['gender'],              
            'city': user_data['city'],             
            'year_of_birth': user_data['year_of_birth'],
            'cours': selected_cours
        }
        
        if st.button("Grade Prediction"):
            grade = predict_user_grade(encoder_regressor, scaler_regressor, X_regressor, model_regressor, user_predict, 'Grade_prediction_model')
            st.write(grade)
        
        if st.button("Certif Prediction"):
            certif = predict_user_certif(encoder_classifier, scaler_classifier, X_classifier, model_classifier, user_predict, 'Certificat_prediction_model')
            st.write(f"{'Yes' if certif == 'Y' else 'Nope'}")


# Barre de navigation
st.sidebar.title("Navigation")
if 'session_username' in st.session_state:
    st.sidebar.write(f"Logged in as {st.session_state['session_username']}")
    if st.sidebar.button("Logout"):
        del st.session_state['session_username']
        st.session_state['page'] = 'Login'
        st.experimental_rerun()
    selected_page = st.sidebar.selectbox("Go to", ["Message", "Certif page"])
    if selected_page == "Message":
        st.session_state['page'] = 'Message'
    elif selected_page == "Certif page":
        st.session_state['page'] = 'Certif page'

else:
    st.sidebar.write("Not logged in")
    choice = st.sidebar.selectbox("Choose Action", ["Login", "Create Account"])
    if choice == "Login":
        st.session_state['page'] = 'Login'
    elif choice == "Create Account":
        st.session_state['page'] = 'Create Account'

# Affichage de la page sélectionnée
if st.session_state['page'] == 'Login':
    login_page()
elif st.session_state['page'] == 'Create Account':
    create_account_page()
elif st.session_state['page'] == 'Message':
    message_page()
elif st.session_state['page'] == "Certif page":
    certif_page()
=======
import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import re
from Sentiment_analysis import translate_and_analyse_sentiment

# MongoDB connection
client = MongoClient('mongodb://localhost:27017')
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
>>>>>>> 74c97c678b7d21b077b1636a308a7826754a9824
