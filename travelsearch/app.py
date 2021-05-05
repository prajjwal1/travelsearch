from flask import Flask, abort, redirect, render_template, request, url_for
import time
import json
import sys
import pickle
import scipy

sys.path.append("../clustering")
from rerankingkmeans import getDocs
from rerankingComplete import getDocsComplete
from rerankingSingle import getDocsSingle

sys.path.append('../index')
from ElasticSearchIndex import Index
from PageRank import PageRank
from RankedModel import RankedModel
from HITS import HITS
from InvertedIndex import InvertedIndex

sys.path.append("../query_expansion")
from association2 import association_main
from metric2 import metric_cluster_main
from scalar2 import scalar_main

# Instantiate Things
app = Flask(__name__)
index1 = Index()

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
    singlelabels = pickle.load(f)
    singlelabels = singlelabels.toarray().ravel()
with open('../index/pages_text.json', 'r') as file:
    pages_text = json.loads(file.read())

# New Home Page
@app.route('/',methods = ['POST', 'GET'])
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
    eq = q # In case page is just refreshed

    # Gets the Query from the Interface
    if request.method == 'POST' and 'query' in request.form:
        q = request.form['query']
        res_algo = request.form['algo_select']
        res_exp = request.form['exp_select']

        # Gets the Algorithm Choice
        if res_algo == "PageRank":
            results = PageRank(index1.query(q)).get_result()
        elif res_algo == "HITS":
            results = HITS(index1.query(q)).get_result()
        elif res_algo == "Vector Space":
            res = index1.query(q)
            results = RankedModel(InvertedIndex(res)).get_result(q, res)
        elif res_algo == "K-Means":
            results = getDocs(q, kmeansvectors, kmeanslabels, kmeanscentroids, kmeansidfs, kmeansterms, kmeansurls)
        elif res_algo == "Single-Link Agglomerative":
            results = getDocsSingle(q, aggvectors, singlelabels, singlecentroids, aggidfs, aggterms, aggurls)
            if len(results) < 10:
                res = index1.query(q)[50:]
                results = RankedModel(InvertedIndex(res)).get_result(q, res)
        elif res_algo == "Complete-Link Agglomerative":
            results = getDocsComplete(q, aggvectors, completelabels, completecentroids, aggidfs, aggterms, aggurls)
            if len(results) < 10:
                res = index1.query(q)[1:85]
                results = RankedModel(InvertedIndex(res)).get_result(q, res)

        # Gets the Query Expansion Choice
        if res_exp == "Associative":
            query_expansion_input = []
            for result in results:
                input_dict = {}
                input_dict['url'] = result['url']
                input_dict['desc'] = pages_text[result['url']]
                query_expansion_input.append(input_dict)
            results = association_main(q, query_expansion_input)
            eq = q  # TODO: FINISH THIS
        elif res_exp == "Metric":
            query_expansion_input = []
            for result in results:
                input_dict = {}
                input_dict['url'] = result['url']
                input_dict['desc'] = pages_text[result['url']]
                query_expansion_input.append(input_dict)
            results =  metric_cluster_main(q, query_expansion_input)           
            eq = q  # TODO: FINISH THIS
        elif res_exp == "Scalar":
            query_expansion_input = []
            for result in results:
                input_dict = {}
                input_dict['url'] = result['url']
                input_dict['desc'] = pages_text[result['url']]
                query_expansion_input.append(input_dict)
            results =  scalar_main(q, query_expansion_input)             
            eq = q  # TODO: FINISH THIS
        else:
            eq = q

        # TODO: REMOVE DEBUG INFO
        print('ALGO: ', res_algo)
        print('EXPANSION: ', res_exp)

    return render_template('search.html', q=q, eq=eq, title=q, time=time.perf_counter()-timeStart, results=results, res_algo=res_algo, res_exp=res_exp)

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
