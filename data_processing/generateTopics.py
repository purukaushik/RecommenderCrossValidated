import gensim
import csv
from gensim import corpora
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
import json

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

def loadTermsFromCSV(path, index=0):
	terms = []
	with open(path, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='"')
		for row in reader:			
			terms.append(row[index])
	return terms

def generateDocument():
	result = db.dbquestion.find()
	questions = [ record['Question_content'] for record in result]
	result = db.dbanswer.find()
	answers = [ record['Answer_content'] for record in result]
	doc = " ".join(questions + answers)
	return doc

	return "I am very new to time series analysis and I couldn't find a satisfying answer on other posts about statistical significance.\nI have 3 times series for 3 distinct stations. Each of them corresponds to an average of 3 distinct measurements and display a striking, coherent change.\nI am asked to present the statistical significance of this change (not to run a significance test) with at least 95% confidence limits on my plots.\nMy  biggest problem is that I am not 100% sure I understand what is expected from me ,and I only one shot to do this. Does that mean I should put the confidence interval based on the measurements used in the average?"

doc = generateDocument()
doc_tokenized = [clean(doc).split()] 
terms = [loadTermsFromCSV("ShortQueryResults.csv")]

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
db.dbtopics.drop()
for key, value in distOfTerms.iteritems():
	if value >= average:
		print key, value
		count += 1
		db.dbtopics.insert({ "name": key, "weightedProbability": value })

print count
#print [y[1].split("*")[0] for y in x]
#print(ldamodel.show_topics(num_topics=10, num_words=1, log=False, formatted=True))

#print(ldamodel.top_topics(doc_clean, num_words=5, log=False, formatted=True))

