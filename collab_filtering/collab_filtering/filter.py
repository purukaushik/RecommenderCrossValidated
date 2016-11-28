# --- Import Libraries --- #

import pandas as pd
from scipy.spatial.distance import cosine
from pymongo import MongoClient

DB = 'dvproject'
POSTS = 'dbpost'
HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'

def getStuffFromRecord(record):
    topics = record.get("topics")
    answers = record.get("answers")
    answerers = map(lambda x: int(x.get("Creater_id")), answers)
    creator = int(record.get("Creater_id"))
    answerers.append(creator)
    return (topics,answerers)

def getFromDB():
    try:
        conn = MongoClient(HOST, 27017)
        collection = conn[DB][POSTS]
        return map(getStuffFromRecord, collection.find())
    except Exception as e:
        print "Mongo Error: terrible shit"
        return None


# Helper function to get similarity scores
def getScore(history, similarities):
    return sum(history * similarities) / sum(similarities)


# TODO: fetch user<-> topic data from mongo, push it to a csv matrix

# --- Read Data --- #
if __name__ == "__main__":

    g = getFromDB()  # g::Cursor
    datadict = dict()
    topicslist = set()
    for topics, answerers in g:
        topic_set= set(topics)
        topicslist.union(topic_set)
        #print topics, answerers
        col = {}
        for answerer in answerers:
            #print answerer
            if answerer not in datadict:
                #print "not in"
                col = dict()
                for topic in topics:
                    col[topic] = 1
            else:
                col = datadict.get(answerer)
                for topic in topics:
                    col[topic] = col.get(topic, 0) + 1
            datadict[answerer] = col
    #print datadict
    topic_data = pd.DataFrame.from_dict(datadict, orient='index').fillna(0)

    data = pd.read_csv('data.csv')
    #print data

    # --- Start Item Based Recommendations --- #
    # Drop any column named "user"
    #topic_data = data.drop('user', 1)
    #print topic_data

    # Create a placeholder dataframe listing item vs. item
    data_ibs = pd.DataFrame(index=topic_data.columns, columns=topic_data.columns)
    #exit()


    # Lets fill in those empty spaces with cosine similarities
    # Loop through the columns
    for i in range(0, len(data_ibs.columns)):
        # Loop through the columns for each column
        for j in range(0, len(data_ibs.columns)):
            # Fill in placeholder with cosine similarities
            data_ibs.ix[i, j] = 1 - cosine(topic_data.ix[:, i], topic_data.ix[:, j])
            print data_ibs.ix[i, j]
    print data_ibs
    # TODO: dump data_ibs to collab_filtering table in mongo
    # # Create a placeholder items for closes neighbours to an item
    # data_neighbours = pd.DataFrame(index=data_ibs.columns, columns=[range(1, 4)])
    #
    # # Loop through our similarity dataframe and fill in neighbouring item names
    # for i in range(0, len(data_ibs.columns)):
    #     data_neighbours.ix[i, :3] = data_ibs.ix[0:, i].order(ascending=False)[:3].index


    # --- End Item Based Recommendations --- #

    # --- Start User Based Recommendations --- #

    # Create a place holder matrix for similarities, and fill in the user name column
    # data_sims = pd.DataFrame(index=data.index, columns=data.columns)
    # data_sims.ix[:, :1] = data.ix[:, :1]
    #
    # # Loop through all rows, skip the user column, and fill with similarity scores
    # for i in range(0, len(data_sims.index)):
    #     for j in range(1, len(data_sims.columns)):
    #         user = data_sims.index[i]
    #         topic = data_sims.columns[j]
    #
    #         if data.ix[i][j] == 1:
    #             data_sims.ix[i][j] = 0
    #         else:
    #             product_top_names = data_neighbours.ix[topic][1:10]
    #             product_top_sims = data_ibs.ix[topic].order(ascending=False)[1:10]
    #             user_interactions = topic_data.ix[user, product_top_names]
    #
    #             data_sims.ix[i][j] = getScore(user_interactions, product_top_sims)
    #
    # # Get the top songs
    # data_recommend = pd.DataFrame(index=data_sims.index, columns=['user', '1', '2', '3', '4', '5', '6'])
    # data_recommend.ix[0:, 0] = data_sims.ix[:, 0]
    #
    # # Instead of top song scores, we want to see names
    # for i in range(0, len(data_sims.index)):
    #     data_recommend.ix[i, 1:] = data_sims.ix[i, :].order(ascending=False).ix[1:7, ].index.transpose()

    # Print a sample
    # print data_recommend.ix[:10, :4]
