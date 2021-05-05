import json
from nltk.tokenize import word_tokenize
from collections import Counter
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
from nltk.corpus import stopwords 
from collections import OrderedDict
import scipy
import pickle
import numpy as np
import multiprocessing
from multiprocessing import Pool, Manager
from bs4 import BeautifulSoup
from itertools import cycle, islice


def check(cluster):
    if len(cluster) < 50:
        return cluster
    else:
        return cluster[:50]

def roundrobin(*iterables):
    num_active = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            num_active -= 1
            nexts = cycle(islice(nexts, num_active))

#function that takes the query and returns the list of document urls
def getDocsComplete(query, vectors, labels, centroids, idfs, terms, urls):

    # with open(r'../clustering/complete/urlsAgg.json') as f:
    #     urls = json.load(f) #list

    #query = query.split()
    queryList = []
    queryList.append(query) #only used for vectorizeing
    # get the vocabulary - should only be done once at the start and then passed to this function 

    #vectorize the query
    vectorizer = TfidfVectorizer(vocabulary = terms, stop_words=stopwords.words('english'), use_idf = False) #produces normalized vectors
    queryVector = vectorizer.fit_transform(queryList) #document - term matrix 
    queryVector = queryVector.toarray()

    # with open(r'../clustering/complete/idfsAgg.pickle', 'rb') as f:
    #     idfs = pickle.load(f) #list 
    #     idfs = idfs.ravel()

    #for i in range (len(queryVector[0])):
    for i in range (np.shape(queryVector)[1]):
        # if queryVector[0,i] != 0:
        #     print(queryVector[0,i], "index : ", i, "term: ", terms[i], "idf: " , idfs[i])
            #muliply the tf with the idf 
        queryVector[0,i] = queryVector[0,i] * idfs[i]

        # if queryVector[0,i] != 0:    
        #     print(queryVector[0,i], "index : ", i, "term: ", terms[i], "idf: " , idfs[i])


    #get the cluster centroids
    # with open(r'../clustering/complete/CAgg.pickle', 'rb') as f:
    #     centroids = pickle.load(f)
    #     centroids = centroids.toarray()

    #compare the query to each centroid and find the closest one (highest score)
    # centroidSim = {}
    # maxSim = 0
    # maxSimCluster = 0# the cluster id that is closest the query
    # maxSimCluster2 = 0
    # i = -1 #cluster id 
    # # for centroid in centroids:
    # i = i + 1
    import itertools
    num_cores = multiprocessing.cpu_count()

    global getCentroid

    def getCentroid(i, centroid, centroidSim):
        sim = cosineSim(queryVector, centroid.reshape(1, -1))
        centroidSim[i] = sim
   
       
        # sim = cosineSim(queryVector, centroid.reshape(1,-1))
        # centroidSim.update({i : sim})
        # if sim > maxSim:
        #     maxSim = sim
        #     maxSimCluster2 = maxSimCluster
        #     maxSimCluster = i

    with multiprocessing.Manager() as manager:
        ns = manager.Namespace()
        ns.centroidSim = manager.dict()
        with manager.Pool(processes=num_cores) as pool:
            pool.starmap(getCentroid, zip(list(range(512)), centroids, itertools.repeat(ns.centroidSim)))

        
            centroidSim = OrderedDict(sorted(ns.centroidSim.items(), key=lambda x: x[1], reverse=True))
    #centroidSim = OrderedDict(sorted(centroidSim.items(), key=lambda x: x[1], reverse=True)) 
    #print("Cluster1: ", maxSimCluster, "Cluster2: ", maxSimCluster2)

    #now compare the docuements in the cluster to the query and rank them
    
    #get the cluster labels
    # with open(r'../clustering/complete/CLAgg.pickle', 'rb') as f:
    #     labels = pickle.load(f)
    #     labels = labels.toarray().ravel()

    # with open(r'../clustering/complete/AggVectors.pickle', 'rb') as f:
    #     vectors = pickle.load(f)
    #     #vectors = vectors.toarray()
    #     vectors = scipy.sparse.csr_matrix(vectors)

            print(vectors.shape)
            print(list(centroidSim)[:5])

            simMap = {}
            l = list(centroidSim)[:5]
            #if a cluster label == maxSimCluster
            i = 0
            
            l = list(centroidSim)[:5]

            cluster1 = check(np.where(labels == l[0])[0])
            #  print(cluster1)
            cluster2 = check(np.where(labels == l[1])[0])
            #  print(cluster2)
            cluster3 = check(np.where(labels == l[2])[0])
            #  print(cluster3)
            cluster4 = check(np.where(labels == l[3])[0])
            #  print(cluster4)
            cluster5 = check(np.where(labels == l[4])[0])
            #  print(cluster5)

            mylist = [cluster1, cluster2, cluster3, cluster4, cluster5]
            li= list(roundrobin(*mylist))

            count = 0

            #for i in range(len(labels)): 
            #     if labels[i] in list(centroidSim)[:5]:
            # #compute the score between the query and the doc in that index
            # #sim = cosineSim(queryVector, vectors[i].reshape(1,-1))
            #         sim = cosineSim(queryVector, vectors.getrow(i).toarray())
             #add teh index in the vector matrix to a index : score map
                    # simMap.update({i : sim}) #all 0 for some reason 
            for element in li:
                sim = cosineSim(queryVector, vectors.getrow(element).toarray())
                simMap.update({element : sim})
                count +=1
                if count == 100:
                    break
            # i = i + 1

            simMap = OrderedDict(sorted(simMap.items(), key=lambda x: x[1], reverse=True))    
    #sort the scores and the for the top 1000, get the indexes (keys)
    #enter those keys into the url list

            returnDocs = []
            j = 0
            for index, score in simMap.items():
                result = {}
                result['url'] = urls[index]
                html_doc = requests.get(urls[index]).text
                soup = BeautifulSoup(html_doc, 'html.parser')
                desc = soup.find("meta", property="og:description")['content']
                title = soup.find("meta", property="og:title")['content']
                if len(desc) > 150:
                    desc = desc[0:150]
                result['title'] = title
                result['desc'] = desc
                returnDocs.append(result)

                if j >= 50: 
                    break
                j = j + 1

    return returnDocs #send docuemnts to user interface with the new ranking 


def cosineSim(queryVector, CDVector):

    dotProduct = 0
    for i in range(len(queryVector[0])):
        dotProduct = dotProduct + (queryVector[0][i] * CDVector[0][i])

    return dotProduct

#reranking the documents and sending back top relevent ones in the cluster

#startTime = datetime.now()
#print(getDocsComplete("san diego zoo"))