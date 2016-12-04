import string

import gensim
from gensim import corpora
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from pymongo import MongoClient
import sys

MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
mongobj = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
db = mongobj.dvproject
QUESTIONS = "dbquestion"
ANSWERS = "dbanswer"
TOPICS = "dbtopics1"
POSTS = "dbposts2"

stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()


def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized


def loadTermsFromDB():
    result = db[TOPICS].find()
    terms = [topic["name"] for topic in result]
    return terms


def generateDocument(question, answers):
    doc = question["Question_content"]
    doc += " ".join(question["Tags"])
    doc += " ".join(answers)
    return doc


terms = [loadTermsFromDB()]
dictionary = corpora.Dictionary(terms)
lda = gensim.models.ldamodel.LdaModel

missedCount = 0
argv = sys.argv
if len(argv) !=3:
    print "Not enough args in call"
    exit()

low,high = argv[1], argv[2]
questionSet = db[QUESTIONS].find({}).sort("Question_id", 1)[int(low):int(high)]
count = 0
#db[POSTS].drop()
posts_q = map(lambda x: x.get("Question_id"), db[POSTS].find({}, {"Question_id": 1}))
for question in questionSet:
    if question.get("Question_id") in posts_q:
        print "Skipping : " + str(question.get("Question_id"))
        continue
    answers = []
    answerObjectList = []
    if question.get("Answer_count") > 0:
        result = db[ANSWERS].find({"Question_id": question["Question_id"]})
        for record in result:
            answers.append(record['Answer_content'])
            answerObjectList.append(record)

    doc = generateDocument(question, answers)
    doc_tokenized = [clean(doc).split()]
    # print (doc_tokenized[0])
    doc_term_matrix = [dictionary.doc2bow(token) for token in doc_tokenized]
    # print doc_term_matrix
    # print doc_term_matrix[0]
    if len(doc_term_matrix[0]) > 0:
        ldamodel = lda(doc_term_matrix, num_topics=100, id2word=dictionary, passes=1000)
        topicModel = ldamodel.print_topics(num_topics=100, num_words=100)

        distOfTerms = {}
        for record in topicModel:
            for word in record[1].split(" + "):
                s = word.split("*")
                if s[1] in distOfTerms:
                    distOfTerms[s[1]] += float(s[0])
                else:
                    distOfTerms[s[1]] = float(s[0])

        termsWeightedList = [(v, k) for k, v in distOfTerms.items()]
        termsWeightedList.sort(reverse=True)

        post = question.copy()
        post["answers"] = answerObjectList
        post["topics"] = [{"name": topic[1], "weight": topic[0]} for topic in termsWeightedList[0:5]]
        print "writing to db..."
        db[POSTS].insert(post)
        print "done writing record " + str(count)
        count += 1
    else:
        print "Missed! :("
        print "Answer count for missed record : " + str(question.get("Answer_count"))
        missedCount += 1

# print "Total Count " + questionSet
print "Missed Count " + str(missedCount)
