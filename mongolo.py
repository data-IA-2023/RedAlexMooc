import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
import dotenv, re, os
import matplotlib.pyplot as plt
import re
import numpy as np

dotenv.load_dotenv()


def _connect_mongo(host, port, db, username=None, password=None, **kwargs):
    """ A utility for making a connection to MongoDB. """
    try:
        if username and password:
            mongo_uri = f'mongodb://{username}:{password}@{host}:{port}/{db}?authSource=admin'
            print(mongo_uri)
            conn = MongoClient(mongo_uri, **kwargs)
        else:
            conn = MongoClient(host, port, **kwargs)
        conn.admin.command('ping')
        return conn[db]
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True, 
               join_collection=None, local_field=None, foreign_field=None, as_field=None, 
               output_collection=None, **kwargs):
    """ Read from MongoDB, optionally join with another collection, and store into DataFrame. """
    try:
        db_conn = _connect_mongo(host=host, port=port, username=username, password=password, db=db, **kwargs)
        if join_collection and local_field and foreign_field and as_field:
            pipeline = [
                {"$match": query},
                {
                    "$lookup": {
                        "from": join_collection,
                        "localField": local_field,
                        "foreignField": foreign_field,
                        "as": as_field
                    }
                }
            ]
            cursor = db_conn[collection].aggregate(pipeline)
        else:
            cursor = db_conn[collection].find(query)
        df = pd.DataFrame(list(cursor))
        if no_id and '_id' in df.columns:
            df.drop('_id', axis=1, inplace=True)
        if output_collection:
            db_conn[output_collection].insert_many(df.to_dict('records'))
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        raise