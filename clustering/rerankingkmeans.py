import json
from nltk.tokenize import word_tokenize
from collections import Counter
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
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
from nltk.corpus import stopwords 
from collections import OrderedDict
import scipy
import pickle
from itertools import cycle, islice
from bs4 import BeautifulSoup
import sys
sys.path.append("../index")
from util import parse_page_html

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

#  maxSim = 0
#  maxSimCluster = 0 # the cluster id that is closest the query
#  maxSimCluster2 = 0
#  i = -1 #cluster id
#  centroidSim = {}

#function that takes the query and returns the list of document urls
def getDocs(query, vectors, labels, centroids, idfs, terms, urls):

    #with open(r'../clustering/kmeans/urlsKmeans.json') as f:
        #urls = json.load(f) #list

    #query = query.split()
    queryList = []
    queryList.append(query) #only used for vectorizeing
    # get the vocabulary - should only be done once at the start and then passed to this function
    # with open(r'../clustering/kmeans/terms.json') as f:
        # terms = json.load(f) #list 

    #vectorize the query
    vectorizer = TfidfVectorizer(vocabulary = terms, stop_words=stopwords.words('english'), use_idf = False) #produces normalized vectors
    queryVector = vectorizer.fit_transform(queryList) #document - term matrix 
    queryVector = queryVector.toarray()

    # with open(r'../clustering/kmeans/idfs.pickle', 'rb') as f:
        # idfs = pickle.load(f) #list 
        # idfs = idfs.ravel()

    for i in range (np.shape(queryVector)[1]):
         # testing purposes to see where the term is in the dictionary
        #  if queryVector[0,i] != 0:
            #  print(queryVector[0,i], "index : ", i, "term: ", terms[i], "idf: " , idfs[i])

        # muliply the tf with the idf 
        queryVector[0,i] = queryVector[0,i] * idfs[i]

        #  if queryVector[0,i] != 0:
            #  print(queryVector[0,i], "index : ", i, "term: ", terms[i], "idf: " , idfs[i])


    #get the cluster centroids
    # with open(r'../clustering/kmeans/C.pickle', 'rb') as f:
    #     centroids = pickle.load(f)
    #     centroids = centroids.toarray()

    #compare the query to each centroid and find the closest one (highest score)
#      maxSim = 0
    #  maxSimCluster = 0 # the cluster id that is closest the query
    #  maxSimCluster2 = 0
    #  i = -1 #cluster id
    #  centroidSim = {}
    import itertools
    num_cores = multiprocessing.cpu_count()

    global getCentroid

    def getCentroid(i, centroid, centroidSim):
            #  centroid_el = self.centroids[centroid_idx]
            #  print(self.centroids.shape)
            #  print(centroid_el)
            #  for i, centroid in enumerate(self.centroids):
            #  for i, centroid in enumerate(centroid_el):
                #  print(self.queryVector.shape, centroid.shape)
        sim = cosineSim(queryVector, centroid.reshape(1, -1))
        centroidSim[i] = sim

    with multiprocessing.Manager() as manager:
        ns = manager.Namespace()
        ns.centroidSim = manager.dict()
        with manager.Pool(processes=num_cores) as pool:
            pool.starmap(getCentroid, zip(list(range(512)), centroids, itertools.repeat(ns.centroidSim)))

    #  _ = Parallel(n_jobs=num_cores)(delayed(centroid_comp.getCentroidSim)(k_val) for k_val in range(len(centroid_comp.centroids)))

            centroidSim = OrderedDict(sorted(ns.centroidSim.items(), key=lambda x: x[1], reverse=True)) 
    #  print("Cluster1: ", maxSimCluster, "Cluster2: ", maxSimCluster2)

    #now compare the docuements in the cluster to the query and rank them

    #get the cluster labels
    # with open(r'../clustering/kmeans/CL.pickle', 'rb') as f:
    #     labels = pickle.load(f)
    #     labels = labels.toarray().ravel()

    # with open(r'../clustering/kmeans/S.pickle', 'rb') as f:
    #     vectors = pickle.load(f)
    #     vectors = scipy.sparse.csr_matrix(vectors)
        #vectors = vectors.toarray()

            print(vectors.shape)
            print(list(centroidSim)[:5])

            simMap = {}
            i = 0

            l = list(centroidSim)[:5]

            #for i in range(5):
            
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

            #x = zip(cluster1, cluster2, cluster3, cluster4, cluster5)
            #print("zip: ",tuple(x))
            count = 0

            
            for element in li:
                sim = cosineSim(queryVector, vectors.getrow(element).toarray())
                simMap.update({element : sim})
                count +=1
                if count == 100:
                    break
            '''       
            for data1, data2, data3 in zip(cluster1, cluster2, cluster3):
                sim1 = cosineSim(queryVector, vectors.getrow(data1).toarray())
                sim2 = cosineSim(queryVector, vectors.getrow(data2).toarray())
                sim3 = cosineSim(queryVector, vectors.getrow(data3).toarray())
                #sim4 = cosineSim(queryVector, vectors.getrow(data4).toarray())
               # sim5 = cosineSim(queryVector, vectors.getrow(data5).toarray())

                simMap.update({data1 : sim1})
                simMap.update({data2 : sim2})
                simMap.update({data3 : sim3})
               # simMap.update({data4 : sim4})
               # simMap.update({data5 : sim5})
                count += 4
                if count == 1000:
                    break'''


            '''
            for i in range(len(labels)): 

                if labels[i] in list(centroidSim)[:5]:
                    #compute the score between the query and the doc in that index
                    sim = cosineSim(queryVector, vectors.getrow(i).toarray())
                     #add the index in the vector matrix to a index : score map
                    simMap.update({i : sim}) 
            '''
            simMap = OrderedDict(sorted(simMap.items(), key=lambda x: x[1], reverse=True))    
            #sort the scores and the for the top 1000, get the indexes (keys)
            #enter those keys into the url list

            returnDocs = []
            j = 0
            for index, score in simMap.items(): #add the top 1000 docs in the cluster to the list to send to UI
                result = {}
                result['url'] = urls[index]
                title, desc = parse_page_html(urls[index])
              
                result['title'] = title
                result['desc'] = desc
                returnDocs.append(result)

                if j >= 50: 
                    break
                j = j + 1

    return returnDocs #send documents to user interface with the new ranking 

def cosineSim(queryVector, CDVector):

    dotProduct = 0
    for i in range(np.shape(queryVector)[1]): 
        dotProduct = dotProduct + (queryVector[0,i] * CDVector[0,i])

    return dotProduct


#startTime = datetime.now()
# print(getDocs("san diego"))

#print("total time = ", datetime.now() - startTime)
