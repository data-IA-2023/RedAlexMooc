from pymongo import MongoClient
from pymongo.errors import CursorNotFound
import dotenv
import os
from tqdm import tqdm
import numpy as np
import pandas as pd 


# Charger les variables d'environnement
dotenv.load_dotenv()

# Connexion MongoDB
client = MongoClient(os.environ["MONGO_URL_LOCALHOST"])
forum = client['RemiGOAT']['MoocMessage']
user = client['RemiGOAT']['User']
#message = client['RemiGOAT']['Message']
userData = client['RemiGOAT']['UserData']
SessionUser = client['RemiGOAT']['SessionUser']
userMessage = client['RemiGOAT']['MessageUser']


# Filter pour université 'CNAM'
filter={
    #'content.course_id': re.compile(r"^MinesTelecom")
}


def EvalSessionExctrateur(doc):
        data ={}
        data['session'] = doc['session']
        if "grade" in doc : 
            while float(doc['grade']) < 0.0:
                    data['IsEval']  = False
            else: 
                    data['IsEval']  = True
        client['RemiGOAT']['Session'].update_one({'session': doc['session']}, {'$set': data}, upsert=True)


for doc in SessionUser.find(filter):
    EvalSessionExctrateur(doc)