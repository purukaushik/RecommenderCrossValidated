import gensim
import csv
from gensim import corpora
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
import json

from pymongo import MongoClient
MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
mongobj = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)
db = mongobj.dvproject
QUESTIONS = "dbquestion"
ANSWERS = "dbanswer"
TOPICS = "dbtopics1"
POSTS = "dbposts"

blackList = ["Autoregressive\\u2013moving-average model", "Lehmann\\u2013Scheff\xe9 theorem", "ruby", "SAS (software)", "untagged", "error", "Python (programming language)",
			 "runs" ]

def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized

def loadTermsFromCSV(path, index=0):
	terms = []
	termsDescMap = {}
	with open(path, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter='|', quotechar='"')		
		for row in reader:
			index = 0
			if len(row) > 0:
				if row[index].strip() == '':
					if len(row) > index+1:
						index+=1
					else:
						continue
				k = row[index].strip()
				if k in blackList:
					continue
				index += 1
				if row[index].strip() == '':
					if len(row) > index + 1:
						index += 1
					else:
						continue
				# print row

				v = row[index].strip()
				terms.append(k)
				termsDescMap[k] = v
				# print v

	return [terms], termsDescMap

def generateDocument():
	result = db[QUESTIONS].find()
	questions = [ record['Question_content'] for record in result]
	result = db[ANSWERS].find()
	answers = [ record['Answer_content'] for record in result]
	doc = " ".join(questions + answers)
	return doc

terms, termsDescMap = loadTermsFromCSV("topicModelling.csv")

try:
	stop = set(stopwords.words('english'))
except Exception:
	import nltk
	nltk.download()
	stop = set(stopwords.words('english'))

print "Done getting stop words"
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()

doc = generateDocument()
doc_tokenized = [clean(doc).split()] 

dictionary = corpora.Dictionary(terms)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_tokenized]

lda = gensim.models.ldamodel.LdaModel
print "Generating lda model..."
ldamodel = lda(doc_term_matrix, num_topics=100, id2word = dictionary, passes=1000)
print "Done lda model"
topicModel = ldamodel.print_topics(num_topics=100, num_words=100)

distOfProbability = {}
distOfTerms= {}

for record in topicModel:
	for word in record[1].split(" + "):
		s = word.split("*")		
		if s[1] in distOfTerms:
			distOfTerms[s[1]] += float(s[0])
		else:
			distOfTerms[s[1]] = float(s[0])

weightedProbability = 0 
for key, value in distOfTerms.iteritems():
	weightedProbability += value

average = weightedProbability / len(distOfTerms.keys())

print "Average: " + str(average)
print "---"*30
count = 0
db[TOPICS].drop()
for key, value in distOfTerms.iteritems():
	if value >= average:
		count += 1
		db[TOPICS].insert({ "name": key[1:-1], "weightedProbability": value, "desc" : termsDescMap.get(key[1:-1]) })

print count
#print [y[1].split("*")[0] for y in x]
#print(ldamodel.show_topics(num_topics=10, num_words=1, log=False, formatted=True))

#print(ldamodel.top_topics(doc_clean, num_words=5, log=False, formatted=True))

