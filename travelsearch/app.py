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

app = Flask(__name__)

# Loads Necessary Data for K-Means Calculations
with open(r'../clustering/kmeans/S.pickle', 'rb') as f:
    kmeansvectors = pickle.load(f)
    kmeansvectors = scipy.sparse.csr_matrix(kmeansvectors)
with open(r'../clustering/kmeans/CL.pickle', 'rb') as f:
    kmeanslabels = pickle.load(f)
    kmeanslabels = kmeanslabels.toarray().ravel()
with open(r'../clustering/kmeans/C.pickle', 'rb') as f:
    kmeanscentroids = pickle.load(f)
    kmeanscentroids = kmeanscentroids.toarray()
with open(r'../clustering/kmeans/idfs.pickle', 'rb') as f:
    kmeansidfs = pickle.load(f) #list 
    kmeansidfs = kmeansidfs.ravel()
with open(r'../clustering/kmeans/terms.json') as f:
    kmeansterms = json.load(f) #list 
with open(r'../clustering/kmeans/urlsKmeans.json') as f:
    kmeansurls = json.load(f) 

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
def search(q=""):
    timeStart = time.perf_counter()

    # Sets eq to be the Expanded Query # TODO: Expand Query
    eq = q 

    # Gets the Query from the Interface
    if request.method == 'POST' and 'query' in request.form:
        q = request.form['query']
        res_algo = request.form['algo_select']
        res_exp = request.form['exp_select']

        # Gets the Query Expansion Choice
        if res_exp == "Associative":
            eq = q #TODO: FINISH THIS
            print("Associative")
        elif res_exp == "Metric":
            eq = q #TODO: FINISH THIS
            print("Metric")
        elif res_exp == "Scalar":
            eq = q #TODO: FINISH THIS
            print("Scalar")
        else:
            res_exp = "No"
        
        # Gets the Algorithm Choice
        if res_algo == "PageRank":
            results = [] #TODO: FINISH THIS
            print("PageRank")
        elif res_algo == "HITS":
            results = [] #TODO: FINISH THIS
            print("HITS")
        elif res_algo == "K-Means":
            results = getDocs(q, kmeansvectors, kmeanslabels, kmeanscentroids, kmeansidfs, kmeansterms, kmeansurls)
        elif res_algo == "Single-Link Agglomerative":
            results = getDocsSingle(q)
        elif res_algo == "Complete-Link Agglomerative":
            results = getDocsComplete(q)
        else:
            res_algo = "Google & Bing"
            results = []
        
        # titles = []
        # for url in results:
        #     titles.append(re.search('<\W*title\W*(.*)</title', requests.get(url).text, re.IGNORECASE).group(1))
        
        # TODO: REMOVE DEBUG INFO
        print('EXPANSION: ', res_exp)
        print('ALGO: ', res_algo)
    else:
        results = []
        res_algo = "Google & Bing"
        res_exp = "No"
    
    # Determines Time to Show Results
    elapsedTime = time.perf_counter() - timeStart

    return render_template('search.html', q=q, eq=eq, title=q, time=elapsedTime, results=results, res_algo=res_algo, res_exp= res_exp)

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