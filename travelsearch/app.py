from flask import Flask, abort, redirect, render_template, request, url_for
import json
import webbrowser
import time

app = Flask(__name__)

# New Home Page
@app.route('/',methods = ['POST', 'GET'])
def index():
   if request.method == 'POST':
      q = request.form['query']
      return redirect(url_for('search', q=q))
   else:
      return render_template('index.html', title="Travel Search")

# Search Page
@app.route('/search/<q>', methods=['GET', 'POST'])
def search(q=""):
    timeStart = time.perf_counter()
    q = q

    # Gets Results for Column #1
    results1 = []
    with open('sampleResults1.json') as f:
        results1 = json.load(f)  # TODO: Load Real Results

    # Gets Results for Column #2
    results2 = []
    with open('sampleResults2.json') as f:
        results2 = json.load(f)  # TODO: Load Real Results
    
    # Gets Results for Column #3
    results3 = []
    with open('sampleResults3.json') as f:
        results3 = json.load(f)  # TODO: Load Real Results

    # Gets Results for Column #4
    results4 = []
    with open('sampleResults4.json') as f:
        results4 = json.load(f)  # TODO: Load Real Results
    
    # Gets the Query from the Interface
    if request.method == 'POST' and 'query' in request.form:
        q = request.form['query']
        return redirect(url_for('search', q=q))
    
    # Determines Time to Show Results
    elapsedTime = time.perf_counter() - timeStart

    webbrowser.open('https://www.google.com/search?q=' + q) # Search Google Simulateously
    webbrowser.open('https://www.bing.com/search?q=' + q)   # Search Bing Simulatenously
    return render_template('search.html', q=q, title=q, time=elapsedTime, results1=results1, results2=results2, results3=results3, results4=results4)

# Handles an Unknown Page
@app.route('/<unknown_page>')
def var_page(unknown_page):
    abort(404)

# 404 Page
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', title="Page Not Found")

if __name__ == '__main__':
    app.run(debug=True)