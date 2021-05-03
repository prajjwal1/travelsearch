import json
from nltk.tokenize import word_tokenize
from collections import Counter
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MiniBatchKMeans
from datetime import datetime
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
from nltk.corpus import stopwords 
from collections import OrderedDict
import scipy
import pickle


#function that takes the query and returns the list of document urls
def getDocs(query):

    with open(r'../clustering/kmeans/urlsKmeans.json') as f:
        urls = json.load(f) #list

    #query = query.split()
    queryList = []
    queryList.append(query) #only used for vectorizeing
    # get the vocabulary - should only be done once at the start and then passed to this function
    with open(r'../clustering/kmeans/terms.json') as f:
        terms = json.load(f) #list 

    #vectorize the query
    vectorizer = TfidfVectorizer(vocabulary = terms, stop_words=stopwords.words('english'), use_idf = False) #produces normalized vectors
    queryVector = vectorizer.fit_transform(queryList) #document - term matrix 
    queryVector = queryVector.toarray()

    
    with open(r'../clustering/kmeans/idfs.pickle', 'rb') as f:
        idfs = pickle.load(f) #list 
        idfs = idfs.ravel()

    for i in range (np.shape(queryVector)[1]):
         #testing purposes to see where the term is in the dictionary
        if queryVector[0,i] != 0:    
            print(queryVector[0,i], "index : ", i, "term: ", terms[i], "idf: " , idfs[i])

        #muliply the tf with the idf 
        queryVector[0,i] = queryVector[0,i] * idfs[i]

        if queryVector[0,i] != 0:    
            print(queryVector[0,i], "index : ", i, "term: ", terms[i], "idf: " , idfs[i])


    #get the cluster centroids
    with open(r'../clustering/kmeans/C.pickle', 'rb') as f:
        centroids = pickle.load(f)
        centroids = centroids.toarray()

    #compare the query to each centroid and find the closest one (highest score)
    centroidSim = {}
    maxSim = 0
    maxSimCluster = 0 # the cluster id that is closest the query
    maxSimCluster2 = 0
    i = -1 #cluster id
    for centroid in centroids:
        i = i + 1
        sim = cosineSim(queryVector, centroid.reshape(1,-1))
        centroidSim.update({i : sim})

        if sim > maxSim:
            maxSim = sim
            maxSimCluster2 = maxSimCluster
            maxSimCluster = i
            
    centroidSim = OrderedDict(sorted(centroidSim.items(), key=lambda x: x[1], reverse=True)) 
    print("Cluster1: ", maxSimCluster, "Cluster2: ", maxSimCluster2)

    #now compare the docuements in the cluster to the query and rank them
    
    #get the cluster labels
    with open(r'../clustering/kmeans/CL.pickle', 'rb') as f:
        labels = pickle.load(f)
        labels = labels.toarray().ravel()

    with open(r'../clustering/kmeans/S.pickle', 'rb') as f:
        vectors = pickle.load(f)
        vectors = scipy.sparse.csr_matrix(vectors)
        #vectors = vectors.toarray()

    print(vectors.shape)
    print(list(centroidSim)[:5])

    simMap = {}
    i = 0
    for i in range(len(labels)): 

        if labels[i] in list(centroidSim)[:5]:
            #compute the score between the query and the doc in that index
            sim = cosineSim(queryVector, vectors.getrow(i).toarray())
             #add teh index in the vector matrix to a index : score map
            simMap.update({i : sim}) 


    simMap = OrderedDict(sorted(simMap.items(), key=lambda x: x[1], reverse=True))    
    #sort the scores and the for the top 1000, get the indexes (keys)
    #enter those keys into the url list

    returnDocs = []
    j = 0
    for index, score in simMap.items(): #add the top 1000 docs in the cluster to the list to send to UI
        returnDocs.append(urls[index])
        if j >= 500: 
            break
        j = j + 1

    return returnDocs #send documents to user interface with the new ranking 

def cosineSim(queryVector, CDVector):

    dotProduct = 0
    for i in range(np.shape(queryVector)[1]): 
        dotProduct = dotProduct + (queryVector[0,i] * CDVector[0,i])

    return dotProduct


#startTime = datetime.now()
#print(getDocs("great wall of china"))

#print("total time = ", datetime.now() - startTime)