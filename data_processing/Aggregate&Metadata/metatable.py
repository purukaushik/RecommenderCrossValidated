import requests,json, re
from pymongo import MongoClient
import math
import re
from datetime import datetime
import ast

MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017

def create_meta():
    client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
    db = client.dvproject
    result = db.dbaggregate0.find()
    count = 0
    full_list = []
    for row in result:
        full_list.append(row)

    # print full_list[0]
    seq = [x['Avg_Question_score'] for x in full_list]
    db.dbmetadata0.insert({"Id" : "Avg_Question_score",
                          "Low" : str(min(seq)) + "-" + str(max(seq)),
                          "Medium" : str(max(seq) / float(3)) + "-" + str(max(seq)),
                            "High" : str(2*(max(seq) / float(3))) + "-" + str(max(seq))})

    support = [x['Support_Percentile'] for x in full_list]
    db.dbmetadata0.insert({"Id": "Support_Percentile",
                           "Low": str(min(support)) + "-" + str(max(support)),
                           "Medium": str(max(support) / float(3)) + "-" + str(max(support)),
                           "High": str(2 * (max(support) / float(3))) + "-" + str(max(support))})

    view = [x['Avg_View_count'] for x in full_list]
    # check = db.dbaggregate0.find({"Avg_View_count": 34630.6666667})
    #
    # for c in check:
    #     print c
    db.dbmetadata0.insert({"Id": "Avg_View_count",
                           "Low": str(min(view)) + "-" + str(max(view)),
                           "Medium": str(max(view) / float(3)) + "-" + str(max(view)),
                           "High": str(2 * (max(view) / float(3))) + "-" + str(max(view))})
    # print min(seq)
    # print max(seq)

if __name__ == '__main__':
    create_meta()