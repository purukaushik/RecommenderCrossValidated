# --- Import Libraries --- #

import pandas as pd
from pymongo import MongoClient, errors
from scipy.spatial.distance import cosine
import json

DB = 'dvproject'
POSTS = 'dbposts0'
HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
RELATED_POSTS = 'dbrelposts0'

def debug(type_):
    print "DEBUG: " + str(type_)


def getStuffFromRecord(record):
    topics = map(lambda x: x.get("name", None), record.get("topics"))
    answers = record.get("answers")
    answers = filter(lambda x: x.get("Creater_id"), answers)
    answerers = map(lambda x: int(x.get("Creater_id")), answers)
    creator_id = record.get("Creater_id")
    question = record.get("Question_id")
    if creator_id:
        creator = int(creator_id)
        answerers.append(creator)
    return topics, answerers


def getFromDB():
    try:
        conn = MongoClient(HOST, 27017)
        collection = conn[DB][POSTS]
        return map(getStuffFromRecord, collection.find())
    except Exception as e:
        print "Error: terrible shit"
        print e.message
        return None


# Helper function to get similarity scores
def getScore(history, similarities):
    return sum(history * similarities) / sum(similarities)

if __name__ == "__main__":

    g = getFromDB()  # g::Cursor
    if not g:
        print "Nothing in DB to process or worse(! :() error!. Exiting..."
        exit()

    datadict = dict()
    topicslist = set()

    for topics, answerers in g:
        topic_set = set(topics)
        topicslist.union(topic_set)
        # print topics, answerers
        col = {}
        for answerer in answerers:
            # print answerer
            if answerer not in datadict:
                # print "not in"
                col = dict()
                for topic in topics:
                    col[topic] = 1
            else:
                col = datadict.get(answerer)
                for topic in topics:
                    col[topic] = col.get(topic, 0) + 1
            datadict[answerer] = col

    topic_data = pd.DataFrame.from_dict(datadict, orient='index').fillna(0)

    data = pd.read_csv('data.csv')

    data_ibs = pd.DataFrame(index=topic_data.columns, columns=topic_data.columns)

    for i in range(0, len(data_ibs.columns)):
        # Loop through the columns for each column
        for j in range(0, len(data_ibs.columns)):
            # Fill in placeholder with cosine similarities
            data_ibs.ix[i, j] = 1 - cosine(topic_data.ix[:, i], topic_data.ix[:, j])
    json_ = json.loads(data_ibs.to_json())
    mongo_ = []

    for k,v in json_.iteritems():
        related_topics = [{"name": str(k_), "value": v_} for k_, v_ in v.iteritems()]

        mongo_.append({"name": str(k), "related_topics": related_topics})

    try:
        conn = MongoClient(HOST, 27017)
        collection = conn[DB][RELATED_POSTS]
        collection.insert(mongo_)
    except errors.PyMongoError as error:
        print "ERROR!: " + error.message