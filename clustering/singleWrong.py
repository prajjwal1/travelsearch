import json
from nltk.tokenize import word_tokenize
from collections import Counter
import requests
#  import pandas as pd
import multiprocessing
from multiprocessing import Pool, Manager
#  from joblib import Parallel, delayed
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
#  import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MiniBatchKMeans
from datetime import datetime
from sklearn.neighbors import NearestCentroid
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk.corpus import stopwords 
from collections import OrderedDict
import scipy
import pickle
from itertools import cycle, islice
from bs4 import BeautifulSoup
import sys
sys.path.append("../index")
from util import parse_page_html, get_result

sys.path.append('../index')
from ElasticSearchIndex import Index


def cosineSim(queryVector, CDVector):

    dotProduct = 0
    for i in range(np.shape(queryVector)[1]): 
        dotProduct = dotProduct + (queryVector[0,i] * CDVector[0,i])

    return dotProduct


def singleWrong(pages_text, query, results):
    
    num_docs = 10
    #results = PageRank(index1.query(q)).get_result()

    docs = []
    urls = []
    for result in results:
        # input_dict = {}
        # input_dict['url'] = result['url']
        # input_dict['desc'] = pages_text[result['url']]
        urls.append(result['page_name'])
        docs.append(pages_text[result['page_name']])    

    if len(docs) == 0: 
        return []
        
    vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), sublinear_tf=True)
    vectors = vectorizer.fit_transform(docs) #document - term matrix 
    terms = vectorizer.get_feature_names()

    queryList = []
    queryList.append(query)
    vectors_distance = 1 - cosine_similarity(vectors)
    vectorizer = TfidfVectorizer(vocabulary = terms, stop_words=stopwords.words('english'), use_idf = False) #produces normalized vectors
    queryVector = vectorizer.fit_transform(queryList) #document - term matrix 
    queryVector = queryVector.toarray()

    vectors_distance = 1 - cosine_similarity(vectors)
    model = AgglomerativeClustering(n_clusters = 15, linkage="single")
    labels = model.fit_predict(vectors_distance) #indexes of the clusters each doc belongs to ndarray (matrix) of shape n_sample
    #centroids = model.cluster_centers_ #(matrix)

    i = -1
    centroidSim = {}

    clf = NearestCentroid()
    #clusters are generated offline before the query is processed
    clf.fit(vectors, labels)
    centroids = clf.centroids_

    for centroid in centroids:
        i = i + 1
        sim = cosineSim(queryVector, centroid.reshape(1,-1))
        centroidSim.update({i : sim})
    
    centroidSim = OrderedDict(sorted(centroidSim.items(), key=lambda x: x[1], reverse=True)) 
    l = list(centroidSim)[:2]
    cluster1 = np.where(labels == l[0])[0]
    cluster2 = np.where(labels == l[1])[0]

    simMap = {}
    for doc in cluster1: 
        sim = cosineSim(queryVector, vectors.getrow(doc).toarray())
             #add teh index in the vector matrix to a index : score map
        simMap.update({doc : sim})
    
    for doc in cluster2: 
        sim = cosineSim(queryVector, vectors.getrow(doc).toarray())
             #add teh index in the vector matrix to a index : score map
        simMap.update({doc : sim}) 

    simMap = OrderedDict(sorted(simMap.items(), key=lambda x: x[1], reverse=True))

    returnDocs = []
    j = 0
    indices = list(simMap.keys())[13:num_docs +13]
    sites = [urls[index] for index in indices]
    returnDocs = get_result(sites)

    return returnDocs 


