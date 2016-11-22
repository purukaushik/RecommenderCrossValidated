import requests,json
from flask import *
import ast
import re

def testing():
    file = open("data1.txt", "r")
    for line in file:
        temp = line
        temp = ast.literal_eval(temp)
        st = temp['Question_content']
        st = re.sub('<[^<]+?>', '', st)
        st = st.replace('\n', '')
        st = re.sub('\$.*?\$', '', st)
        temp['Question_content'] = st
        print temp['Question_content']
        print temp['tags']


if __name__ == '__main__':
    testing()