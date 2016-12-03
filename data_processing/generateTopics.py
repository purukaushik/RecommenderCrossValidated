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
TOPICS = "dbtopics"
POSTS = "dbposts"


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
			if len(row) > 0:
				k = row[index].strip()
				v = row[index+1].strip()
				terms.append(k)
				termsDescMap[k] = v
	return [terms], termsDescMap

def generateDocument():
	result = db[QUESTIONS].find()
	questions = [ record['Question_content'] for record in result]
	result = db[ANSWERS].find()
	answers = [ record['Answer_content'] for record in result]
	doc = " ".join(questions + answers)
	return doc

terms, termsDescMap = loadTermsFromCSV("topicModelling.csv")

stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()

doc = generateDocument()
doc_tokenized = [clean(doc).split()] 

dictionary = corpora.Dictionary(terms)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_tokenized]

lda = gensim.models.ldamodel.LdaModel
ldamodel = lda(doc_term_matrix, num_topics=100, id2word = dictionary, passes=1000)
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
		print key, value
		count += 1
		print { "name": key, "weightedProbability": value, "desc" : termsDescMap.get(key) }
		exit()
		# db[TOPICS].insert({ "name": key, "weightedProbability": value, "desc" : termsDescMap.get(key) })

print count
#print [y[1].split("*")[0] for y in x]
#print(ldamodel.show_topics(num_topics=10, num_words=1, log=False, formatted=True))

#print(ldamodel.top_topics(doc_clean, num_words=5, log=False, formatted=True))

