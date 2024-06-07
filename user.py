from pymongo import MongoClient
from pymongo.errors import CursorNotFound
import dotenv
import os
from tqdm import tqdm
import numpy as np


# Charger les variables d'environnement
dotenv.load_dotenv()

# Connexion MongoDB
client = MongoClient(os.environ["MONGO_URL_LOCALHOST"])
#forum = client['RemiGOAT']['Forum']
user = client['RemiGOAT']['User']
#message = client['RemiGOAT']['Message']
userData = client['RemiGOAT']['UserData']
SessionUser = client['RemiGOAT']['SessionUser']


# Filter pour université 'CNAM'
filter={
    #'content.course_id': re.compile(r"^MinesTelecom")
}

def usernameExtracteur(doc):
    data = {
        'country': None,
        'gender': None,
        'year_of_birth': None,
        'CSP': None,
        'level_of_education': None,
        'city': None,
        'email': None
        }
    username = doc.get('username', None)
    id       = doc.get('_id',None)
    if not username:
        return  # Ignore the document if username is None or empty
    data['id'] = id
    data['username'] = username
    client['RemiGOAT']['UserData'].update_one({'username': doc['username']}, {'$set': data}, upsert=True)

"""with user.find(no_cursor_timeout=True) as cursor:
        for doc in tqdm(cursor):
                usernameExtracteur(doc)"""
      


# Définir la connexion MongoDB
client = MongoClient(os.environ["MONGO_URL_LOCALHOST"])
db = client['RemiGOAT']
user_collection = db['UserData']

def userExtracteur(doc):
    data = {
        'country': None,
        'gender': None,
        'year_of_birth': None,
        'CSP': None,
        'level_of_education': None,
        'city': None,
        'email': None
    }

    for value in doc.values():
        if isinstance(value, dict):
            if 'country' in value and data['country'] is None:
                data['country'] = value['country']
            if 'gender' in value and data['gender'] is None:
                data['gender'] = value['gender']
            if 'year_of_birth' in value and data['year_of_birth'] is None:
                data['year_of_birth'] = int(value['year_of_birth']) if value['year_of_birth'].isdigit() else None
            if 'CSP' in value and data['CSP'] is None:
                data['CSP'] = value['CSP']
            if 'level_of_education' in value and data['level_of_education'] is None:
                data['level_of_education'] = value['level_of_education']
            if 'city' in value and data['city'] is None:
                data['city'] = value['city']
            if 'email' in value and data['email'] is None:
                data['email'] = value['email']

    if 'username' in doc:
        print(doc['username'])
        #print(data)
        user_collection.update_one(
            {'username': doc['username']}, 
            {'$set': data}, 
            upsert=True
        )
    else:
        print("Username not found in document.")


def gradeExtracteur(doc):
    username = doc.get('username', None)
    id       = doc.get('_id',None)
    if not username:
        return  # Ignore the document if username is None or empty
    
    # Parcourir les champs pour extraire les informations pertinentes
    data = {}
    data['username'] = username
    data['id'] = id
    for  value in doc.items():
                if isinstance(value[1], dict):
                    data = {}
                    
                    data['username'] = username

                    data['idUser'] = id

                    data['session'] = value[0]

                    if "Certificate Delivered" in value[1]: 
                        data['Certificate Delivered'] = value[1]["Certificate Delivered"]   

                    if "Certificate Eligible" in value[1]: 
                        data['Certificate Eligible'] = value[1]["Certificate Eligible"]

                    if "Certificate Type" in value[1]: 
                        data['Certificate Type'] = value[1]["Certificate Type"]

                    if "Enrollment Track" in value[1]:
                        data['Enrollment Track'] = value[1]["Enrollment Track"]

                    if "Cohort Name" in value[1]: 
                        data['Cohort Name'] = value[1]["Cohort Name"]   

                    if "date_grade_report" in value[1]:
                        data['date_grade_report'] = value[1]["date_grade_report"]

                    if "date_problem_grade_report" in value[1]:
                        data['date_problem_grade_report'] = value[1]["date_problem_grade_report"]

                    if "grade" in value[1]: 
                        data['grade'] = value[1]["grade"]    

                    if "Verification Status" in value[1]:
                        data['Verification Status'] = value[1]["Verification Status"]

                    SessionUser.insert_one(data)


def process_documents():
    batch_size = 50  # Taille du lot définie à 50
    skip = 0
    continue_processing = True

    while continue_processing:
        try:
            docs_processed = 0
            with user.find(no_cursor_timeout=True).skip(skip).limit(batch_size) as cursor:
                for doc in tqdm(cursor):
                    gradeExtracteur(doc)
                    docs_processed += 1

            if docs_processed < batch_size:
                continue_processing = False  # Terminer le traitement si moins de documents que la taille du lot ont été traités
            else:
                skip += docs_processed  # Mettre à jour skip pour continuer là où on s'est arrêté

        except CursorNotFound:
            print(f"Cursor not found at skip {skip}, retrying from the same position with batch size {batch_size}...")
            # Ne pas mettre à jour skip pour recommencer le lot courant
            continue

process_documents()

# Fermer la connexion client lorsqu'on a terminé
client.close()