import json
from nltk.tokenize import word_tokenize
from collections import Counter
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MiniBatchKMeans
from datetime import datetime
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer 
import scipy
import pickle
import re

def readJson(): #read the crawled documents and return the matrix of docuement vectors 

    with open(r'../crawl/travel.json') as f:
        data = json.load(f) #list of dictionaries
    
   
    #tokenize the text ----------------------------------------------------------------------
    docs = []
    urls = []
    lemmatizer = WordNetLemmatizer()

    for element in data: #each element is a dict (each element is a document/webpage)
        
        if re.search(r".*SiteIndex*", element["url_to"]) != None:
            print(element["url_to"])
            continue
        if re.search(r".*sitemaps*", element["url_to"]) != None:
            print(element["url_to"])
            continue

        tokens = word_tokenize(element["text"]) #tokenize

        document = ' '.join([lemmatizer.lemmatize(w) for w in tokens]) #lemmatize each word in the doc

        docs.append(document) #add the doc to the list

        urls.append(element["url_to"]) #add the url to the list

    # compute the document vectors 
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), sublinear_tf=True)
    vectors = vectorizer.fit_transform(docs) #document - term matrix 

    print(vectors.shape)
    terms = vectorizer.get_feature_names() #.index(value) to get the index of a value; gets the terms in array form

    with open('terms.json', 'w') as outfile:
        json.dump(terms, outfile)

    with open('urlsKmeans.json', 'w') as outfile:
        json.dump(urls, outfile)

    idfs = vectorizer.idf_
    file = open("idfs.pickle",'wb')
    pickle.dump(idfs, file)
    
    return vectors


vectors = readJson()

#document vectors
sparse_repr = scipy.sparse.csr_matrix(vectors)
file = open("S.pickle",'wb')
pickle.dump(sparse_repr, file)

