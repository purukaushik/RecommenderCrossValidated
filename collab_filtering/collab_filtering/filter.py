#!/usr/env/python
import json

import pandas as pd
from pymongo import MongoClient, errors
from scipy.spatial.distance import cosine

DB = 'dvproject'
POSTS = 'dbposts1'
HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
RELATED_POSTS = 'dbrelposts1'
COSINE_POSTS = 'dbrelcosineposts1'


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
    return topics, answerers, question


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


def collab_filter(topic_map):
    """
    Performs collab filtering on dict containing either users<->Topics or questions<->Topics

    :return: a JSON containing the collab filtering matrix metrics
    for each topic nad related topics
    """
    topic_data = pd.DataFrame.from_dict(topic_map, orient='index').fillna(0)
    data = pd.read_csv('data.csv')
    data_ibs = pd.DataFrame(index=topic_data.columns, columns=topic_data.columns)
    for i in range(0, len(data_ibs.columns)):
        # Loop through the columns for each column
        for j in range(0, len(data_ibs.columns)):
            # Fill in placeholder with cosine similarities
            data_ibs.ix[i, j] = 1 - cosine(topic_data.ix[:, i], topic_data.ix[:, j])
    json_ = json.loads(data_ibs.to_json())
    return json_


def mongo_write_json(json_result, collectionName):
    mongo_ = []
    debug("Building json for mongodb on " + collectionName)
    for k, v in json_result.iteritems():
        related_topics = [{"name": str(k_), "value": v_} for k_, v_ in v.iteritems()]
        mongo_.append({"name": str(k), "related_topics": related_topics})
    debug("Connecting to mongo on " + HOST + ":" + "27017")
    try:
        conn = MongoClient(HOST, 27017)
        collection = conn[DB][collectionName]
        debug("Dropping stuff in collection " + collectionName)
        collection.remove({})
        debug("Inserting prepared stuff in collection " + collectionName)
        collection.insert(mongo_)
    except errors.PyMongoError as error:
        print "ERROR!: " + error.message


if __name__ == "__main__":

    g = getFromDB()  # g::Cursor
    if not g:
        print "Nothing in DB to process or worse(! :() error!. Exiting..."
        exit()

    userTopicMap = dict()
    topicsList = set()
    questionTopicMap = dict()

    for topics, answerers, question in g:
        topic_set = set(topics)
        topicsList.union(topic_set)

        col = {}
        col_ = {}
        for topic in topics:
            col_[topic] = 1
            questionTopicMap[question] = col_

        for answerer in answerers:

            if answerer not in userTopicMap:

                col = dict()
                for topic in topics:
                    col[topic] = 1
            else:
                col = userTopicMap.get(answerer)
                for topic in topics:
                    col[topic] = col.get(topic, 0) + 1
            userTopicMap[answerer] = col
    debug("Running collab filtering on userTopicMap")
    mongo_write_json(collab_filter(userTopicMap), collectionName=RELATED_POSTS)

    debug("Running collab filtering on questionTopicMap")
    mongo_write_json(collab_filter(questionTopicMap), collectionName=COSINE_POSTS)
