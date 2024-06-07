import os
import sys
import torch
from transformers import BertTokenizer, BertModel
from sklearn import preprocessing
import numpy as np
from dotenv import load_dotenv
# sys.path.append("modules")
# from check_enc import *
import pymongo
import pandas as pd
from torchmetrics.functional import pairwise_cosine_similarity


load_dotenv()
mongo_url=os.environ.get('MONGOURL') # the url connexion string

client = pymongo.MongoClient(mongo_url)
db = client["RemiGOAT"]
collection_msg = db["Message"]
collection_forum = db["Forum"]
collection_thread_embed = db["ThreadEmbed"]


# Load the BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
model = BertModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')





# text = "This is an example sentence."
def get_sentence_embedding(text:str,tokenizer,model):
    # Preprocess the input text
    inputs = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=512,
        return_attention_mask=True,
        return_tensors='pt'
    )
    # Get the BERT embeddings
    outputs = model(**inputs)
    last_hidden_states = outputs.last_hidden_state

    # Extract the sentence embedding
    sentence_embedding = torch.mean(last_hidden_states, dim=1)
    return sentence_embedding[0]

def meta_function_embedding(tokenizer,model):
    return lambda text : get_sentence_embedding(text,tokenizer,model)


def concat_vector_embeddings(L1:list[str],L2:list[str],tokenizer,model):
    x=torch.cat(tuple([get_sentence_embedding(e,tokenizer,model) for e in L1]),dim=0)
    y=torch.cat(tuple([get_sentence_embedding(e,tokenizer,model) for e in L2]),dim=0)
    return x,y

def self_concat_vector_embeddings_np(L:list[str],tokenizer,model):
    x=np.array([get_sentence_embedding(e,tokenizer,model).detach().numpy().tolist() for e in L])
    return x

def most_similar(L1:list[str],L2:list[str],tokenizer,model):
    x,y=concat_vector_embeddings(L1,L2,tokenizer,model)
    a=pairwise_cosine_similarity(x, y)
    print(a)
    return torch.argmax(a, dim=1)




def find_thread(sentence:str,tokenizer,model)->str:
    """## finds a thread wich corresponds to the sentence

    ### Args:
        - `sentence (str)`: the sentec
        - `tokenizer (_type_)`: the tokenizer
        - `model (_type_)`: the model

    ### Returns:
        - `str`: the id of the thread
    """
    global collection_thread_embed
    k=0
    similarity={}
    test_sentence_embedding=get_sentence_embedding(sentence, tokenizer, model)
    for x in collection_thread_embed.find():
        _id=x["_id"]
        similarity[_id]=torch.nn.functional.cosine_similarity(torch.tensor(x["embed_vector"]),test_sentence_embedding,0).item()
        print(similarity[_id])
    L=list(similarity.values())
    m=max(range(len(L)), key=L.__getitem__)
    max_id=list(similarity.keys())[m]
    return max_id

def find_thread_message(thread_id:str,sentence:str,tokenizer,model)->str:
    """## Finds the closest massge to the senctence in a thread

    ### Args:
        - `thread_id (str)`: the thread id of the thread to search in
        - `sentence (str)`: the sentenc to search
        - `tokenizer (_type_)`: the tokenizer
        - `model (_type_)`: the model to use

    ### Returns:
        - `str`: the id of the closest message in the thread
    """
    global collection_msg
    k=0
    similarity={}
    test_sentence_embedding=get_sentence_embedding(sentence, tokenizer, model)
    for x in collection_msg.find({'thread_id':thread_id}):
        _id=x["message_id"]
        similarity[_id]=torch.nn.functional.cosine_similarity(get_sentence_embedding(x["body"],tokenizer,model),test_sentence_embedding,0).item()
        print(similarity[_id])
    L=list(similarity.values())
    m=max(range(len(L)), key=L.__getitem__)
    max_id=list(similarity.keys())[m]
    return max_id

def faq(sentence:str,tokenizer,model)->str:
    """## _summary_

    ### Args:
        - `sentence (str)`: the sentence to search
        - `tokenizer (_type_)`: the tokenizer
        - `model (_type_)`: the model

    ### Returns:
        - `str`: the id of a similar message
    """
    thread_id=find_thread(sentence,tokenizer,model)
    _id=find_thread_message(thread_id,sentence, tokenizer, model)
    return _id

if __name__=="__main__":
    id_=faq("Je souhaite apprendre", tokenizer, model)
    print(id_)
    exit()