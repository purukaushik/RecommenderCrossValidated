import requests,json
from flask import *
import ast
import re
from pymongo import MongoClient
import os

mongobj = MongoClient()
db = mongobj.dvproject

def adding_related_database(temp, i):
    try:
        related_list = temp['related_list']
        for item in related_list:
            temp_rel = item
            rt = temp_rel['related_ques_content']
            if rt is not None:
                rt = re.sub('<[^<]+?>', '', rt)
                rt = rt.replace('\n', '')
                rt = re.sub('\$.*?\$', '', rt)
                temp_rel['related_ques_content'] = rt

            db.dbrelated.insert({'Question_id': temp['question_id'],
                                 'Related_ques_content': temp_rel['related_ques_content'],
                                 'Related_ques_title': temp_rel['related_ques_title'],
                                 'Tags': temp_rel['tags']})
    except:
        print 'Error Occured when adding the Realted question for Question ID - ' + temp['question_id'] + 'Data file number - ' + str(i)


def adding_answer_database(temp, i):
    try:
        answer_list = temp['answers_list']
        for item in answer_list:
            temp_ans = item
            at = temp_ans['answer_content']
            if at is not None:
                at = re.sub('<[^<]+?>', '', at)
                at = at.replace('\n', '')
                at = re.sub('\$.*?\$', '', at)
                temp_ans['answer_content'] = at

            db.dbanswer.insert({'Question_id': temp['question_id'],
                                'Start_date': temp_ans['start_date'],
                                'Last_activity': temp_ans['last_activity'],
                                'Answer_content': temp_ans['answer_content'],
                                'Creator_reputation': temp_ans['creator_reputation'],
                                'Last_activity': temp_ans['last_activity'],
                                'Creater_id': temp_ans['creater_id'],
                                'Question_score': temp_ans['question_score'],
                                'Display_name': temp_ans['display_name']})
    except:
        print 'Error Occured when adding the answer for Question ID - ' + temp['question_id'] + 'Data file number - ' + str(i)

def adding_question_database(temp, i):
    try:
        qt = temp['Question_content']
        if qt is not None:
            qt = re.sub('<[^<]+?>', '', qt)
            qt = qt.replace('\n', '')
            qt = re.sub('\$.*?\$', '', qt)
            temp['Question_content'] = qt
        db.dbquestion.insert({'Question_id': temp['question_id'],
                              'Start_date': temp['start_date'],
                              'Link': temp['link'],
                              'Last_activity': temp['last_activity'],
                              'Creator_reputation': temp['creator_reputation'],
                              'Last_activity': temp['last_activity'],
                              'Creater_id': temp['creater_id'],
                              'Answer_count': temp['answer_count'],
                              'Question_content': temp['Question_content'],
                              'Question_score': temp['question_score'],
                              'Display_name': temp['display_name'],
                              'Tags': temp['tags'],
                              'View_count': temp['view_count']})
    except:
        print 'Error Occured when adding the question for Question ID - ' + temp['question_id'] + 'Data file number - ' + str(i)

Global_repeating_question = 0
def exporting_to_mongo():
    # Creating the objects for the Mongo DB
    global Global_repeating_question
    for i in range(1, 20):
        if os.path.isfile('data' + str(i) + '.txt'):
            print 'Running file ' + str(i)
            file = open("data"+ str(i) +".txt", "r")
            for line in file:
                temp = line
                temp = ast.literal_eval(temp)
                check = db_question_exists(temp['question_id'])
                if check == False:
                    # Adding contents into the Question Database
                    adding_question_database(temp, i)

                    answer_count = temp['answer_count']
                    if answer_count > 0:
                        # Adding contents into the Answer Database
                        adding_answer_database(temp, i)

                    related_list = temp['related_list']
                    if len(related_list) > 0:
                        # Adding contents into the Related Question Database
                        adding_related_database(temp, i)
                else:
                    Global_repeating_question += 1
                    print 'The question id - ' + str(temp['question_id']) + ' has been repeated.'

        else:
            print 'File number ' + str(i) + ' does not exist.'
    #  Iterating over the files


def db_question_exists(recipient):
    mongobj = MongoClient()
    db = mongobj.dvproject
    result = db.dbquestion.find({"Question_id": recipient})
    count = result.count()
    if count == 0:
        return False
    else:
        return True

if __name__ == '__main__':
    exporting_to_mongo()
    # testing()