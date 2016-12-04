import requests,json, re
from pymongo import MongoClient
import math
import re
from datetime import datetime
import ast

MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017

question_dict = {}
client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
db = client.dvproject
full = db.dbquestion.find()
for each in full:
    question_dict[each["Question_id"]] = each


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def get_title(question_id):
    return question_dict[question_id]["Title"]


def list_computation(target_list, value, question_id, link):
    title = get_title(question_id)
    target_list.append({"Question_id": question_id, "Link": link, "Value": value, "Title": title})
    # target_list = sorted(target_list, key = lambda x: x.get("Value"), reverse = True)
    return target_list

def adding_list(row, temp_dict):
    temp_dict["View_Question_list"] = list_computation(temp_dict["View_Question_list"], row["View_count"], row["Question_id"], row["Link"])
    temp_dict["Score_Question_list"] = list_computation(temp_dict["Score_Question_list"], row["Question_score"], row["Question_id"], row["Link"])
    if not row["answers"]:
        temp_dict["Bounty_Question_list"] = list_computation(temp_dict["Bounty_Question_list"], row["Question_score"], row["Question_id"], row["Link"])
    else:
        temp_dict["Most_Answer_Question_list"] = list_computation(temp_dict["Most_Answer_Question_list"], row["Answer_count"], row["Question_id"], row["Link"])
    temp_dict["Recent_Question_list"] = list_computation(temp_dict["Recent_Question_list"], row["Start_date"].split(' ')[0], row["Question_id"], row["Link"])
    return temp_dict

def new_topic_entry(row):
    temp_dict = {}
    q_date_list = row["Start_date"].split(' ')[0]
    q_date_list = q_date_list.split('-')[0]
    temp_year = {}
    ques_year_dict = {}
    time_diff = 0
    if not row["answers"]:
        temp_dict["Question_unanswered"] = 1
        temp_dict["Question_answered"] = 0
        temp_dict["No_of_Answer_Count"] = 0
        ques_year_dict["Question_unanswered"] = 1
        ques_year_dict["Question_answered"] = 0
    else:
        temp_dict["Question_unanswered"] = 0
        temp_dict["Question_answered"] = 1
        temp_dict["No_of_Answer_Count"] = row["Answer_count"]
        ques_year_dict["Question_unanswered"] = 0
        ques_year_dict["Question_answered"] = 1
        qtemp = row["Start_date"].split(' ')
        atemp = row["answers"][0]["Start_date"].split(' ')
        time_diff = days_between(qtemp[0], atemp[0])
        time_diff = int(time_diff) * 24
        qtime = row["Start_date"].split(' ')[1]
        atime = row["answers"][0]["Start_date"].split(' ')[1]
        if int(qtime.split(':')[0]) < int(atime.split(':')[0]):
            time_diff = time_diff + (int(atime.split(':')[0]) - int(qtime.split(':')[0]))
        else:
            time_diff = time_diff + (int(qtime.split(':')[0]) - int(atime.split(':')[0]))
    temp_dict["Response_Time"] = time_diff
    temp_dict["Avg_View_count"] = row["View_count"]
    temp_dict["Avg_Question_score"] = row["Question_score"]
    temp_year[q_date_list] = ques_year_dict
    temp_dict["Year"] = temp_year
    temp_dict["View_Question_list"] = []
    temp_dict["Score_Question_list"] = []
    temp_dict["Most_Answer_Question_list"] = []
    temp_dict["Bounty_Question_list"] = []
    temp_dict["Recent_Question_list"] = []
    temp_dict = adding_list(row, temp_dict)
    return temp_dict

def existing_topic(row, aggregate_dict, topic):
    temp_dict = aggregate_dict[topic]
    q_date_list = row["Start_date"].split(' ')[0]
    q_date_list = q_date_list.split('-')[0]
    temp_year = temp_dict["Year"]
    if q_date_list in temp_year.keys():
        ques_year_dict = temp_year[q_date_list]
    else:
        ques_year_dict = {"Question_unanswered": 0, "Question_answered": 0}
    time_diff = 0
    if not row["answers"]:
        temp_dict["Question_unanswered"] = temp_dict["Question_unanswered"] + 1
        temp_dict["Question_answered"] = temp_dict["Question_answered"] + 0
        temp_dict["No_of_Answer_Count"] = temp_dict["No_of_Answer_Count"] + 0
        ques_year_dict["Question_unanswered"] = ques_year_dict["Question_unanswered"] + 1
        ques_year_dict["Question_answered"] = ques_year_dict["Question_answered"] + 0
    else:
        temp_dict["Question_unanswered"] = temp_dict["Question_unanswered"] + 0
        temp_dict["Question_answered"] = temp_dict["Question_answered"] + 1
        temp_dict["No_of_Answer_Count"] = temp_dict["No_of_Answer_Count"] + row["Answer_count"]
        ques_year_dict["Question_unanswered"] = ques_year_dict["Question_unanswered"] + 0
        ques_year_dict["Question_answered"] = ques_year_dict["Question_answered"] + 1
        qtemp = row["Start_date"].split(' ')
        atemp = row["answers"][0]["Start_date"].split(' ')
        time_diff = days_between(qtemp[0], atemp[0])
        time_diff = int(time_diff) * 24
        qtime = row["Start_date"].split(' ')[1]
        atime = row["answers"][0]["Start_date"].split(' ')[1]
        if int(qtime.split(':')[0]) < int(atime.split(':')[0]):
            time_diff = time_diff + (int(atime.split(':')[0]) - int(qtime.split(':')[0]))
        else:
            time_diff = time_diff + (int(qtime.split(':')[0]) - int(atime.split(':')[0]))
    temp_dict["Response_Time"] = temp_dict["Response_Time"] + time_diff
    temp_dict["Avg_View_count"] = temp_dict["Avg_View_count"] + row["View_count"]
    temp_dict["Avg_Question_score"] = temp_dict["Avg_Question_score"] + row["Question_score"]
    temp_year[q_date_list] = ques_year_dict
    temp_dict["Year"] = temp_year
    temp_dict = adding_list(row, temp_dict)
    return temp_dict


def aggregate_script():
    client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
    db = client.dvproject
    result = db.dbposts0.find()
    aggregate_dict = {}
    count = 0
    for row in result:
        # print row
        count = count + 1
        print count
        topics = row["topics"]
        for topic in topics:
            topic = topic["name"]
            if topic in aggregate_dict.keys():
                temp_dict = existing_topic(row, aggregate_dict, topic)
            else:
                temp_dict = new_topic_entry(row)
            aggregate_dict[topic] = temp_dict
        # print aggregate_dict
    return aggregate_dict


def testing():
    client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
    db = client.dvproject
    result = db.dbposts0.find()
    aggregate_dict = {}
    print result[12]

def testing2(question_id):
    client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
    db = client.dvproject
    result = db.dbquestion.find({"Question_id" : 246872})
    print result

def recompute(full_dict):
    for temp in full_dict.keys():
        each = full_dict[temp]
        each["Avg_Question_score"] = each["Avg_Question_score"] / float(each["Question_unanswered"] + each["Question_answered"])
        if each["Avg_View_count"] > 1000:
            print each["Avg_View_count"], each["Question_unanswered"], each["Question_answered"]
        each["Avg_View_count"] = each["Avg_View_count"] / float(each["Question_unanswered"] + each["Question_answered"])

        if each["Avg_View_count"] > 1000:
            print each["Avg_View_count"], each["Question_unanswered"], each["Question_answered"]

        if each["Question_answered"] == 0:
            each["Avg_Answer_count"] = 0
        else:
            each["Avg_Answer_count"] = each["No_of_Answer_Count"] / float(each["Question_answered"])

        each["Support_Percentile"] = each["Question_answered"] / float(each["Question_unanswered"] + each["Question_answered"])
        each["Support_Percentile"] = each["Support_Percentile"] * 100

        temp_list = each["View_Question_list"]
        temp_list = sorted(temp_list, key=lambda x: x.get("Value"), reverse=True)
        each["View_Question_list"] = temp_list[:5]

        temp_list = each["Score_Question_list"]
        temp_list = sorted(temp_list, key=lambda x: x.get("Value"), reverse=True)
        each["Score_Question_list"] = temp_list[:5]

        temp_list = each["Bounty_Question_list"]
        temp_list = sorted(temp_list, key=lambda x: x.get("Value"), reverse=True)
        each["Bounty_Question_list"] = temp_list[:5]

        temp_list = each["Most_Answer_Question_list"]
        temp_list = sorted(temp_list, key=lambda x: x.get("Value"), reverse=True)
        each["Most_Answer_Question_list"] = temp_list[:5]

        temp_list = each["Recent_Question_list"]
        # sorted(timestamps, key=lambda d: map(int, d.split('-')))
        temp_list = sorted(temp_list, key=lambda x: x.get("Value"), reverse=True)
        each["Recent_Question_list"] = temp_list[:5]
        print each["Avg_View_count"], temp, each["View_Question_list"]
        full_dict[temp] = each

    return full_dict

def add_to_db(final):
    client = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
    db = client.dvproject
    for each in final.keys():
        temp = final[each]
        db.dbaggregate0.insert({
                                "Topic": each,
                                "Question_unanswered": temp["Question_unanswered"],
                                "Recent_Question_list": temp["Recent_Question_list"],
                                "Avg_Question_score": temp["Avg_Question_score"],
                                "Score_Question_list": temp["Score_Question_list"],
                                "View_Question_list": temp["View_Question_list"],
                                "Avg_View_count": temp["Avg_View_count"],
                                "Bounty_Question_list": temp["Bounty_Question_list"],
                                "No_of_Answer_Count": temp["No_of_Answer_Count"],
                                "Most_Answer_Question_list": temp["Most_Answer_Question_list"],
                                "Year": temp["Year"],
                                "Avg_Answer_count": temp["Avg_Answer_count"],
                                "Support_Percentile": temp["Support_Percentile"],
                                "Response_Time": temp["Response_Time"],
                                "Question_answered": temp["Question_answered"]})


if __name__ == '__main__':
    full_dict = aggregate_script()
    final = recompute(full_dict)
    # print final
    add_to_db(final)
