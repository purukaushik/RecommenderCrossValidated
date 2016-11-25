import gensim
import csv
from gensim import corpora
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
import string
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



doc = "I am very new to time series analysis and I couldn't find a satisfying answer on other posts about statistical significance.\nI have 3 times series for 3 distinct stations. Each of them corresponds to an average of 3 distinct measurements and display a striking, coherent change.\nI am asked to present the statistical significance of this change (not to run a significance test) with at least 95% confidence limits on my plots.\nMy  biggest problem is that I am not 100% sure I understand what is expected from me ,and I only one shot to do this. Does that mean I should put the confidence interval based on the measurements used in the average?"
doc_clean = clean(doc)
doc_cleaned = [clean(doc_clean).split()] 
print doc 
#terms = [loadTermsFromCSV("QueryResults.csv")]
terms = ["statistical time series significance analysis test".split()]

dictionary = corpora.Dictionary(terms)
doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_cleaned]

lda = gensim.models.ldamodel.LdaModel
ldamodel = lda(doc_term_matrix, num_topics=8, id2word = dictionary, passes=1000)
x = ldamodel.print_topics(num_topics=8, num_words=1)
print [y[1].split("*")[0] for y in x]
#print(ldamodel.show_topics(num_topics=10, num_words=1, log=False, formatted=True))

#print(ldamodel.top_topics(doc_clean, num_words=5, log=False, formatted=True))

