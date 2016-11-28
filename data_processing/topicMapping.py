import gensim
import csv
from gensim import corpora
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string

from pymongo import MongoClient

mongobj = MongoClient()
db = mongobj.dvproject

stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()

def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

def loadTermsFromDB():
	result = db.topics.find()
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

questionSet = db.dbquestion.find()
for question in questionSet:
	print question["Question_id"]
	answers = []
	answerObjectList = []
	if question.get("Answer_count") > 0:
		result = db.dbanswer.find({"Question_id" : question["Question_id"]})
		for record in result: 
			answers.append(record['Answer_content'])
			answerObjectList.append(record)

	doc = generateDocument(question, answers)
	doc_tokenized = [clean(doc).split()] 	
	
	doc_term_matrix = [dictionary.doc2bow(token) for token in doc_tokenized]
	if len(doc_term_matrix[0]) > 0:
		ldamodel = lda(doc_term_matrix, num_topics=100, id2word = dictionary, passes=1000)
		topicModel = ldamodel.print_topics(num_topics=100, num_words=100)

		distOfTerms= {}
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
		post["topics"] = [ {"name": topic[1], "weight": topic[0]} for topic in termsWeightedList[0:5] ]
		db.dbposts.insert(post)	
	else:
		missedCount += 1

#print "Total Count " + questionSet
print "Missed Count " + str(missedCount)
			

