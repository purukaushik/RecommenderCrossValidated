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
    q_list = resp_dres.get('items')
    comp_list = []
    if q_list:
        for i in q_list:
            temp = i
            comp_dict = {}
            #print temp
            comp_dict['view_count'] = temp.get('view_count')
            comp_dict['link'] = temp.get('link')
            comp_dict['answer_count'] = temp.get('answer_count')
            comp_dict['question_score'] = temp.get('score')
            last_activity = temp.get('last_activity_date')
            if last_activity :
                last_activity = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_activity))
                comp_dict['last_activity'] = last_activity
            start_date = temp.get('creation_date')
            if start_date:
                start_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_date))
                comp_dict['start_date'] = start_date

            comp_dict['Question_content'] = temp.get('body')
            comp_dict['Title'] = temp.get('title')
            comp_dict['question_id'] = temp.get('question_id')
            comp_dict['tags'] = temp.get('tags')
            try:
                owner = temp.get('owner')
                if owner:
                    comp_dict['creater_id'] = owner.get('user_id')
                    comp_dict['creator_reputation'] = owner.get('reputation')
                    comp_dict['display_name'] = owner.get('display_name')
            except:
                pass
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
                        temp_a_dict['answer_content'] = temp_a.get('body')
                        temp_a_dict['question_score'] = temp_a.get('score')
                        last_activity = temp_a.get('last_activity_date')
                        if last_activity:
                            last_activity = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_activity))
                            temp_a_dict['last_activity'] = last_activity
                        start_date = temp_a.get('creation_date')
                        if start_date:
                            start_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_date))
                            temp_a_dict['start_date'] = start_date
                        owner = temp_a.get('owner')
                        if owner:
                            temp_a_dict['creater_id'] = owner.get('user_id')
                            temp_a_dict['creator_reputation'] = owner.get('reputation')
                            temp_a_dict['display_name'] = owner.get('display_name')
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
                            temp_b_dict['related_ques_content'] = temp_b.get('body')
                            temp_b_dict['tags'] = temp_b.get('tags')
                            temp_b_dict['related_ques_title'] = temp_b.get('title')
                            related_lt.append(temp_b_dict)
            comp_dict['related_list'] = related_lt
            comp_dict['answers_list'] = answer_lt
            # print comp_dict
            comp_list.append(comp_dict)

    f.close()
    print len(comp_list)

    datafile = 'data' + var + '.txt'
    data = open(datafile, 'w')
    for item in comp_list:
        data.write("%s\n" % item)
    data.close()
    if len(comp_list):
        callscp(datafile)
        #callscp(datafile)
        f = open('Counter.txt', 'w')
        var = int(var) + 1
        f.write(str(var))
        f.close()


def testing_2():
    url = "https://api.stackexchange.com/2.2/questions?site=stats&filter=withbody"
    #url = "https://api.stackexchange.com/2.2/questions/245551/answers?site=stats&filter=withbody"
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
    #count_ln()
    for i in range(3):
        testing()
