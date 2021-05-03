# Travel Search
**Information Retrieval Class Project - Group #4**

A complete search engine, optimized for travel, built using Python 3 by the talented developers below

#### Authors
|         Section |        Developer        | GitHub                                         |
|----------------:|:-----------------------:|------------------------------------------------|
|        Crawling |    Prajjwal Bhargava    | [@prajjwal1](https://github.com/prajjwal1)     |
|        Indexing |       Brian Nguyen      | [@briannoogin](https://github.com/briannoogin) |
|       Interface |        Caleb Hoff       | [@CrunchyCat](https://github.com/CrunchyCat)   |
|      Clustering |        Autumn Pin       | [@pin-a](https://github.com/pin-a)             |
| Query Expansion | Swamynathan Singaravelu | [@ssMD16](https://github.com/ssMD16)           |

#### Installing Dependencies
```
$ pip3 install -r requirements.txt
$ pip3 install scikit-learn scipy matplotlib pandas nltk

$ python 
$ import nltk
$ nltk.download('stopwords')
$ nltk.download('punkt')
$ ntlk.download('wordnet')
$ exit
```

## 1. Crawling
> Maintainer: [@prajjwal1](https://github.com/prajjwal1)

```
$ cd crawl
$ scrapy crawl travel -O travel.json
```
The crawled result would appear in travel.json. Each json file has two attributes `url` (indicating what page to show while displaying results) and `text` (we will use this to perform indexing).
If you want to use `jsonl` format, inside `crawl` directory use,
```
$ python3 get_jsonl.py
```

## 2. Indexing
> Maintainer: [@briannoogin](https://github.com/briannoogin)

After web pages are crawled, they are indexed and the links they contain are analyzed.

## 3. Interface
> Maintainer: [@CrunchyCat](https://github.com/CrunchyCat)

```
$ cd travelsearch
$ python app.py
```
The interface is made using Flask and is displayed in a web browser.

## 4. Clustering
> Maintainer: [@pin-a](https://github.com/pin-a)

Web pages are clustered and used to improve the relevance of search results.
```
$ cd clustering
$ python AggVectorize.py
$ python kmeanVectorize.py

The two programs generate the document vectors and other information necessary for clustering and generating results. The files termsAgg.json, urlsAgg.json, idfsAgg.pickle, and AggVectors.pickle are created from the AggVectorize.py program and should be placed in clustering/complete. The files terms.json, urlsKmeans.json, idfs.pickle, and S.pickle are created from the kmeansVectorize.py program and should be placed in the clustering/kmeans. 

$ cd kmeans 
$ python clusteringKmean

The documents are clustered using mini batch kmeans and the files CL.pickle (cluster labels for each document) and C.pickle (centroids of each cluster) are generated. 

$ cd ../complete 
$ python clusteringAgg.py

The documents are clustered using complete link agglomerative clustering and the files CLAgg.pickle (cluster labels for each document) and CAgg.pickle (centroids of each cluster) are generated. 

$ cd ../single 
$ python clusteringAggSingle.py

The documents are clustered using single link agglomerative clustering and the files CLAggSingle.pickle (cluster labels for each document) and CAggSingle.pickle (centroids of each cluster) are generated. 

When a query is asked through the user interface rerankingkmeans.py, rerankingComplete.py, and rerankingSingle.py are called and the results are presented. 
```
## 5. Query Expansion
> Maintainer: [@ssMD16](https://github.com/ssMD16)

Query Expansion is used to provide relevant results to the user.
