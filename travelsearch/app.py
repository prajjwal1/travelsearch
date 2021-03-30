from flask import Flask, abort, redirect, render_template, request, url_for
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
    if request.method == 'POST' and 'query' in request.form:
        q = request.form['query']
        return redirect(url_for('search', q=q))
    return render_template('search.html', q=q, title=q)

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