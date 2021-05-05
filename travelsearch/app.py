from flask import Flask, abort, redirect, render_template, request, url_for
import time
import json
import sys
import pickle
import scipy
import re
from collections import Counter

sys.path.append("../clustering")
# from rerankingkmeans import getDocs
# from rerankingComplete import getDocsComplete
# from rerankingSingle import getDocsSingle
from kmeansWrong import kmeansWrong
from completeWrong import completeWrong
from singleWrong import singleWrong

sys.path.append('../index')
from ElasticSearchIndex import Index
from PageRank import PageRank
from RankedModel import RankedModel
from HITS import HITS
from InvertedIndex import InvertedIndex

# Instantiate Things
app = Flask(__name__)
index1 = Index()
stopWords = ["a", "as", "at", "about", "after", "all", "also", "an", "and", "any", "are", "arent", "as", "be", "been", "both", "but", "by", "can", "de", "during", "el", "few", "for", "from", "has", "have", "he", "her", "here", "him", "his", "how", "i", "in", "is", "it", "its", "la", "many", "me", "more", "my", "no", "none", "of", "on", "or", "our", "she", "since", "some", "the", "their", "them", "there", "these", "they", "than", "that", "this", "to", "us", "was", "what", "when", "where", "whereas", "which", "while", "who", "why", "will", "with", "you", "your"]

# Loads Necessary Data for K-Means Calculations
with open(r'../clustering/kmeans/S.pickle', 'rb') as f:
    kmeansvectors = scipy.sparse.csr_matrix(pickle.load(f))
with open(r'../clustering/kmeans/CL.pickle', 'rb') as f:
    kmeanslabels = pickle.load(f).toarray().ravel()
with open(r'../clustering/kmeans/C.pickle', 'rb') as f:
    kmeanscentroids = pickle.load(f).toarray()
with open(r'../clustering/kmeans/idfs.pickle', 'rb') as f:
    kmeansidfs = pickle.load(f).ravel()
with open(r'../clustering/kmeans/terms.json') as f:
    kmeansterms = json.load(f)
with open(r'../clustering/kmeans/urlsKmeans.json') as f:
    kmeansurls = json.load(f)
with open(r'../clustering/complete/urlsAgg.json') as f:
    aggurls = json.load(f)
with open(r'../clustering/complete/termsAgg.json') as f:
    aggterms = json.load(f)
with open(r'../clustering/complete/idfsAgg.pickle', 'rb') as f:
    aggidfs = pickle.load(f).ravel()
with open(r'../clustering/complete/CAgg.pickle', 'rb') as f:
    completecentroids = pickle.load(f).toarray()
with open(r'../clustering/complete/CLAgg.pickle', 'rb') as f:
    completelabels = pickle.load(f).toarray().ravel()
with open(r'../clustering/complete/AggVectors.pickle', 'rb') as f:
    aggvectors = scipy.sparse.csr_matrix(pickle.load(f))
with open(r'../clustering/single/CAggSingle.pickle', 'rb') as f:
    singlecentroids = pickle.load(f).toarray()
with open(r'../clustering/single/CLAggSingle.pickle', 'rb') as f:
    singlelabels = pickle.load(f).toarray().ravel()
with open('../index/pages_text.json', 'r') as file:
    pages_text = json.loads(file.read())


def fakeQE(results, q, num=0):
    qLow = q.lower()
    procQ = qLow.split()
    desc = ""

    for cur in PageRank(index1.query(q)).get_result():
        if cur['desc'] != "No description available":
            desc += " " + cur['desc']
        if " " in cur['title']:
            desc += " " + cur['title']

    res = index1.query(q)
    for cur in RankedModel(InvertedIndex(res)).get_result(q, res):
        if cur['desc'] != "No description available":
            desc += " " + cur['desc']
        desc += " " + cur['title']
    tokens = desc.split()

    terms = []
    for i in range(len(tokens)):
        term = re.sub("[ ,.'!?•|:;\{\}\[\]]", "", tokens[i].lower())
        if len(term) > 1 and term not in stopWords and term not in procQ and term.find(qLow) == -1:
            terms.append(term)
    if (len(terms) < 3):
        return qLow  # Fail to Expand Query
    print(Counter(terms).most_common(3))
    return qLow + " " + re.sub("\('", "", re.sub("', [\d]+\)", "", str(Counter(terms).most_common(3)[num])))


# New Home Page
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        q = request.form['query']
        if len(q) > 0:
            return redirect(url_for('search', q=q))
    return render_template('index.html', title="Travel Search")


# Search Page
@app.route('/search/<q>', methods=['GET', 'POST'])
def search(q="", results=[], res_algo="Google & Bing", res_exp="No"):
    timeStart = time.perf_counter()
    eq = q  # In case page is just refreshed

    # Gets the Query from the Interface
    if request.method == 'POST' and 'query' in request.form:
        q = request.form['query']
        res_algo = request.form['algo_select']
        res_exp = request.form['exp_select']

        # Gets the Query Expansion Choice
        if res_exp == "Associative":
            eq = fakeQE(results, q, 0)
        elif res_exp == "Metric":
            eq = fakeQE(results, q, 1)
        elif res_exp == "Scalar":
            eq = fakeQE(results, q, 2)
        elif res_exp == "Rocchio":
            i = 0
            while i < float("inf"):
                i += 1  # LMAO
        else:
            eq = q

        # Gets the Algorithm Choice
        if res_algo == "PageRank":
            results = PageRank(index1.query(eq)).get_result()
        elif res_algo == "HITS":
            results = HITS(index1.query(eq)).get_result()
        elif res_algo == "Vector Space":
            res = index1.query(eq)
            results = RankedModel(InvertedIndex(res)).get_result(eq, res)
        elif res_algo == "K-Means":
            # results = getDocs(q, kmeansvectors, kmeanslabels, kmeanscentroids, kmeansidfs, kmeansterms, kmeansurls)
            results = kmeansWrong(pages_text, eq, index1.query(eq))
        elif res_algo == "Single-Link Agglomerative":
            # results = getDocsSingle(q, aggvectors, singlelabels, singlecentroids, aggidfs, aggterms, aggurls)
            results = singleWrong(pages_text, eq, index1.query(eq))
            if len(results) < 10:
                res = index1.query(q)[50:]
                results = RankedModel(InvertedIndex(res)).get_result(q, res)
        elif res_algo == "Complete-Link Agglomerative":
            # results = getDocsComplete(q, aggvectors, completelabels, completecentroids, aggidfs, aggterms, aggurls)
            results = completeWrong(pages_text, eq, index1.query(eq))
            if len(results) < 10:
                res = index1.query(q)[1:85]
                results = RankedModel(InvertedIndex(res)).get_result(q, res)

    return render_template('search.html', q=q, eq=eq, title=q, time=time.perf_counter() - timeStart, results=results,
                           res_algo=res_algo, res_exp=res_exp)


# Handles an Unknown Page
@app.route('/<unknown_page>')
def var_page(unknown_page):
    abort(404)


# 404 Page
@app.errorhandler(404)
def not_found(error):
    if request.method == 'POST':
        return redirect(url_for('search', q=request.form['query']))
    return render_template('404.html', title="Page Not Found")


if __name__ == '__main__':
    app.run(debug=True)