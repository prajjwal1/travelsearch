import json
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import scipy
import pickle
from datetime import datetime
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.neighbors import NearestCentroid
from sklearn.metrics.pairwise import cosine_similarity
import scipy.cluster.hierarchy as sch


startTime = datetime.now()

#get the document vectors from the file 
#with open(r'../complete/AggVectors.pickle', 'rb') as f:
    #vectors = pickle.load(f)

with open('AggVectors.pickle', 'rb') as f:
    vectors = pickle.load(f)
    #vectors = vectors.toarray()

vectors_distance = 1 - cosine_similarity(vectors) #distances
#linkage_matrix = sch.linkage(vectors_distance, method='single')
clusterer = AgglomerativeClustering(n_clusters = 512, linkage="single")
clusterLabels = clusterer.fit_predict(vectors_distance)

print(clusterer.n_clusters_)

# Plot dendrogram
#fig, ax = plt.subplots() 
#ax = sch.dendrogram(linkage_matrix, orientation="right", labels=)
#plt.tight_layout()
#plt.savefig('dendrogramSingle.png')

clf = NearestCentroid()
clf.fit(vectors, clusterLabels)
centroids = clf.centroids_

#cluster labels 
sparse_repr = scipy.sparse.csr_matrix(clusterLabels)
file = open("CLAggSingle.pickle",'wb')
pickle.dump(sparse_repr, file)

#centroid vectors
sparse_repr = scipy.sparse.csr_matrix(centroids)
file = open("CAggSingle.pickle",'wb')
pickle.dump(sparse_repr, file)