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


def messageExtracteur(doc):
        data ={}
        if 'username' in  doc:
                data['message_id'] = doc['id']
                if doc['type'] == 'thread':
                    data['parent_id']        = doc['id']
                    data['thread_id']        = doc['id']
                    data['thread_type']      =  doc['thread_type']
                    data['title']            =  doc['title']
                    data['context']          = doc['context']
                    if 'courseware_title' in doc:
                        data['courseware_title'] =  doc['courseware_title']
                elif doc['depth'] ==0 :
                    data['thread_id']        = doc['thread_id']
                    data['parent_id']        = doc['thread_id']
                else : 
                    data['thread_id']        = doc['thread_id']
                    data['parent_id']        = doc['parent_id']
                     

                data['course_id']        = doc['course_id']
                data['username']         = doc['username']
                data['body']             = doc['body']
                data['type']             = doc['type']
                data['created_at']       = doc['created_at']
                data['updated_at']       = doc['updated_at']
                data['vote_down_count']  = doc['votes']['down_count']
                data['vote_up_count']    = doc['votes']['up_count']
                data['vote_point']       = doc['votes']['point']
                data['vote_count']       = doc['votes']['count']
                userMessage.insert_one(data)
                if 'children' in doc:
                    for resp in doc['children']:
                        messageExtracteur(resp)
                if 'non_endorsed_response' in doc:
                    for resp in doc['non_endorsed_response']:
                        messageExtracteur(resp)
        else: 
             pass




for doc in forum.find(filter):
    messageExtracteur(doc['content'])