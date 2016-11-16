import requests,json, re
from flask import *
import time
import os


def callscp(datafile):
    try:
        os.system("scp -i \"ec2svr1.pem\" "+ datafile +" ec2-user@ec2-52-43-158-164.us-west-2.compute.amazonaws.com:~/data/")
    except Exception as e:
        print  "Move ec2svr1.pem from gmail to RecommenderCrossValidated/data_collections folder"

def testing():
    f = open('Counter.txt', 'r')
    var = f.read()
    print "Counter: " + var
    url = "https://api.stackexchange.com/2.2/questions?site=stats&filter=withbody&pagesize=100&page=" + var
    resp = requests.get(url)
    resp_dres = resp.json()
    #print resp_dres
    q_list = resp_dres['items']
    comp_list = []
    for i in q_list:
        temp = i
        comp_dict = {}
        comp_dict['view_count'] = temp['view_count']
        comp_dict['link'] = temp['link']
        comp_dict['answer_count'] = temp['answer_count']
        comp_dict['question_score'] = temp['score']
        last_activity = temp['last_activity_date']
        last_activity = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_activity))
        comp_dict['last_activity'] = last_activity
        start_date = temp['creation_date']
        start_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_date))
        comp_dict['start_date'] = start_date
        comp_dict['Question_content'] = temp['body']
        comp_dict['Title'] = temp['title']
        comp_dict['question_id'] = temp['question_id']
        comp_dict['tags'] = temp['tags']
        answer_lt = []
        related_lt = []
        if comp_dict['answer_count'] > 0:
            url_a = "https://api.stackexchange.com/2.2/questions/" + str(comp_dict['question_id']) + "/answers?site=stats&filter=withbody"
            resp = requests.get(url_a)
            resp_dres = resp.json()
            if 'items' in resp_dres:
                a_list = resp_dres['items']
                for j in a_list:
                    temp_a = j
                    #print temp_a
                    temp_a_dict = {}
                    temp_a_dict['answer_content'] = temp_a['body']
                    temp_a_dict['question_score'] = temp_a['score']
                    last_activity = temp_a['last_activity_date']
                    last_activity = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_activity))
                    temp_a_dict['last_activity'] = last_activity
                    start_date = temp_a['creation_date']
                    start_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_date))
                    temp_a_dict['start_date'] = start_date
                    temp_a_dict['creater_id'] = temp_a['owner']['user_id']
                    temp_a_dict['creator_reputation'] = temp_a['owner']['reputation']
                    temp_a_dict['display_name'] = temp_a['owner']['display_name']
                    answer_lt.append(temp_a_dict)
                # /questions/{ids}/related
                url_b = "https://api.stackexchange.com/2.2/questions/" + str(comp_dict['question_id']) + "/related?site=stats&filter=withbody"
                resp_b = requests.get(url_b)
                resp_b = resp_b.json()
                if 'items' in resp_b:
                    b_list = resp_b['items']
                    for k in b_list:
                        temp_b = k
                        temp_b_dict ={}
                        temp_b_dict['related_ques_content'] = temp_b['body']
                        temp_b_dict['tags'] = temp_b['tags']
                        temp_b_dict['related_ques_title'] = temp_b['title']
                        related_lt.append(temp_b_dict)
        comp_dict['related_list'] = related_lt
        comp_dict['answers_list'] = answer_lt
        print comp_dict
        comp_list.append(comp_dict)

    f.close()
    print comp_list

    datafile = 'data' + var + '.txt'
    data = open(datafile, 'w')
    for item in comp_list:
        data.write("%s\n" % item)
    data.close()

    callscp(datafile)
    f = open('Counter.txt', 'w')
    var = int(var) + 1
    f.write(str(var))
    f.close()


def testing_2():
    # url = "https://api.stackexchange.com/2.2/questions?site=stats&filter=withbody"
    url = "https://api.stackexchange.com/2.2/questions/245551/answers?site=stats&filter=withbody"
    resp = requests.get(url)
    resp_dres = resp.json()
    print resp_dres


def count_ln():
    url_b = "https://api.stackexchange.com/2.2/tags?site=stats&filter=withbody&pagesize=100&page=1"
    resp_b = requests.get(url_b)
    resp_b = resp_b.json()
    print resp_b

if __name__ == '__main__':
    #testing_2()
    # count_ln()
    for i in range(3):
        testing()

