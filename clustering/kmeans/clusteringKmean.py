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

startTime = datetime.now()

#vectors = readJson()

with open('S.pickle', 'rb') as f:
    vectors = pickle.load(f)#Each row of variable vectors is a vector representation of a doc

'''
sse = {}
for k in range(75, 100):
    kmeans = KMeans(n_clusters=k, max_iter=1000).fit(vectors)
    labels = kmeans.labels_
    #print(data["clusters"])
    sse[k] = kmeans.inertia_ # Inertia: Sum of distances of samples to their closest cluster center
plt.figure()
plt.plot(list(sse.keys()), list(sse.values()))
plt.xlabel("Number of cluster")
plt.ylabel("SSE")
plt.show()'''

true_k = 512

model = MiniBatchKMeans(init='k-means++', n_clusters=true_k, n_init=10, max_no_improvement=10, verbose=0)
print("cluster time : ", datetime.now() - startTime)
clusterLabels = model.fit_predict(vectors) #indexes of the clusters each doc belongs to ndarray (matrix) of shape n_sample
#docs_cl=pd.DataFrame(list(zip(title,labels)),columns=['title','cluster'])
#print(docs_cl.sort_values(by=['cluster']))
centroids = model.cluster_centers_ #(matrix)

#cluster labels 
sparse_repr = scipy.sparse.csr_matrix(clusterLabels)
file = open("CL.pickle",'wb')
pickle.dump(sparse_repr, file)

#centroid vectors
sparse_repr = scipy.sparse.csr_matrix(centroids)
file = open("C.pickle",'wb')
pickle.dump(sparse_repr, file)