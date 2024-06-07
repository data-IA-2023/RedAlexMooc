from pymongo import MongoClient
import dotenv
import os
from tqdm import tqdm

# Charger les variables d'environnement
dotenv.load_dotenv()

# Connexion MongoDB
client = MongoClient(os.environ["MONGO_URL_LOCALHOST"])
#forum = client['RemiGOAT']['Forum']
user = client['RemiGOAT']['User']
#message = client['RemiGOAT']['Message']
userData = client['RemiGOAT']['UserData']


# Filter pour université 'CNAM'
filter={
    #'content.course_id': re.compile(r"^MinesTelecom")
}



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
                if 'country' in value.keys():
                    data['country'] = value['country']
                if 'gender' in value.keys():
                        data['gender'] = value['gender']
                if 'year_of_birth' in value.keys():
                        data['year_of_birth'] = int(value['year_of_birth']) if value['year_of_birth'].isdigit() else None
                if 'CSP' in value.keys():
                        data['CSP'] = value['CSP']
                if 'level_of_education' in value.keys():
                        data['level_of_education'] = value['level_of_education']
                if 'city' in value.keys():
                        data['city'] = value['city']
                if 'email' in value.keys():
                        data['email'] = value['email']

           # client['RemiGOAT']['UserData'].update_one({'id': data['id']}, {'$set': data}, upsert=True)



# Boucle sur tous les fils de discution du CNAM
for doc in tqdm(user.find()):
    gradeExtracteur(doc)
from pymongo import MongoClient
import dotenv
import os
from tqdm import tqdm

# Charger les variables d'environnement
dotenv.load_dotenv()

# Connexion MongoDB
client = MongoClient(os.environ["MONGO_URL_LOCALHOST"])
#forum = client['RemiGOAT']['Forum']
user = client['RemiGOAT']['User']
#message = client['RemiGOAT']['Message']
userData = client['RemiGOAT']['UserData']


# Filter pour université 'CNAM'
filter={
    #'content.course_id': re.compile(r"^MinesTelecom")
}



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
                if 'country' in value.keys():
                    data['country'] = value['country']
                if 'gender' in value.keys():
                        data['gender'] = value['gender']
                if 'year_of_birth' in value.keys():
                        data['year_of_birth'] = int(value['year_of_birth']) if value['year_of_birth'].isdigit() else None
                if 'CSP' in value.keys():
                        data['CSP'] = value['CSP']
                if 'level_of_education' in value.keys():
                        data['level_of_education'] = value['level_of_education']
                if 'city' in value.keys():
                        data['city'] = value['city']
                if 'email' in value.keys():
                        data['email'] = value['email']

           # client['RemiGOAT']['UserData'].update_one({'id': data['id']}, {'$set': data}, upsert=True)



# Boucle sur tous les fils de discution du CNAM
for doc in tqdm(user.find()):
    gradeExtracteur(doc)