import json
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords 
from datetime import datetime
import pickle
import re
from random import seed, randint


with open(r'../crawl/travel.json') as f:
    data = json.load(f) #list of dictionaries

#tokenize the text ----------------------------------------------------------------------
docs = []
urls = []
lemmatizer = WordNetLemmatizer()

seed(1)
for element in data: #each element is a dict (each element is a document/webpage)

    if randint(1,9) != 9:#choose a random number 1-8
        continue

    if re.search(r".*SiteIndex*", element["url_to"]) != None:
        print(element["url_to"])
        continue
    if re.search(r".*sitemaps*", element["url_to"]) != None:
        print(element["url_to"])
        continue
    #remove airbnb and tripadvisor    
    if re.match("https://www.tripadvisor.com*", element["url_to"]):
        continue
    if re.match("https://airbnb.com*", element["url_to"]):
        continue

    tokens = word_tokenize(element["text"]) #tokenize

    document = ' '.join([lemmatizer.lemmatize(w) for w in tokens]) #lemmatize each word in the doc

    docs.append(document) #add the doc to the list

    urls.append(element["url_to"]) #add the url to the list   

with open("urlsAgg.json", "w") as outfile:
    json.dump(urls, outfile)

# compute the document vectors 
vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), sublinear_tf = True) 
vectors = vectorizer.fit_transform(docs) #document - term matrix 

print(vectors.shape)
terms = vectorizer.get_feature_names() #.index(value) to get the index of a value; gets the terms in array form

with open('termsAgg.json', 'w') as outfile:
    json.dump(terms, outfile)

idfs = vectorizer.idf_
file = open("idfsAgg.pickle",'wb')
pickle.dump(idfs, file)

sparse_repr = scipy.sparse.csr_matrix(vectors)
file = open("AggVectors.pickle",'wb')
pickle.dump(sparse_repr, file)

