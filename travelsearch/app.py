from flask import Flask, abort, redirect, render_template, request, url_for
import json
import webbrowser

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
    q = q

    with open('../crawl/travel.json') as f:
        results = json.load(f)  # TODO: Load Real Results

    # Use Query (q) and Results (results) to show correct results in UI

    if request.method == 'POST' and 'query' in request.form:
        q = request.form['query']
        return redirect(url_for('search', q=q))
    
    webbrowser.open('https://www.google.com/search?q=' + q) # Search Google Simulateously
    webbrowser.open('https://www.bing.com/search?q=' + q)   # Search Bing Simulatenously
    return render_template('search.html', q=q, title=q, results=results)

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