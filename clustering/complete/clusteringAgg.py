import json
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import re
import scipy
import pickle
from datetime import datetime
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.neighbors import NearestCentroid
from sklearn.metrics.pairwise import cosine_similarity


startTime = datetime.now()

#get the document vectors from the file 
with open('AggVectors.pickle', 'rb') as f:
    vectors = pickle.load(f)
    #vectors = vectors.toarray()

#Each row of variable vectors is a vector representation of a doc
# Hence, we can use vectors as input for the k-means algorithm

# # cluster the document vectors
#vectors.toarray()


#dendo = linkage(vectors, method="complete", metric = "cosine")
#vectors_distance = cosine_similarity(vectors, dense_output = False) #distances
#linkage_matrix = sch.linkage(vectors_distance, method='complete')
vectors_distance = 1 - cosine_similarity(vectors)
#linkage_matrix = sch.linkage(vectors_distance, method='complete')
clusterer = AgglomerativeClustering(n_clusters = 512, linkage="complete") #only creates 2 clusters (n clusters)
clusterLabels = clusterer.fit_predict(vectors_distance)

# Plot dendrogram
#fig, ax = plt.subplots() 
#ax = sch.dendrogram(linkage_matrix, orientation="right", labels=title)
#plt.tight_layout()
#plt.savefig('dendrogramComplete.png')

print(clusterer.n_clusters_)
#names_clusters_20 = {n: c for n, c in zip(cols, clusterLabels)}
#calculate the mean of he vectors in each cluster to get the centroids

#clusterLabels=clusterer.labels_
#docs_cl=pd.DataFrame(list(zip(title,labels)),columns=['title','cluster'])
#print(docs_cl.sort_values(by=['cluster']))
#centroids  = clustering.cluster_centers_  #means of shape [10,] 

clf = NearestCentroid()
#clusters are generated offline before the query is processed
clf.fit(vectors, clusterLabels)
centroids = clf.centroids_

print(centroids)
#cluster labels 
sparse_repr = scipy.sparse.csr_matrix(clusterLabels)
# Try executing `S`
file = open("CLAgg.pickle",'wb')
pickle.dump(sparse_repr, file)

#centroid vectors
sparse_repr = scipy.sparse.csr_matrix(centroids)
# Try executing `S`
file = open("CAgg.pickle",'wb')
pickle.dump(sparse_repr, file)

print("total time = ", datetime.now() - startTime)
