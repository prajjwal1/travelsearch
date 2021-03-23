from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    searchedQuery = ""
    if request.method == 'POST' and 'query' in request.form:
        searchedQuery = request.form['query']
    return render_template('index.html', searchedQuery=searchedQuery)

if __name__ == '__main__':
    app.run(debug=True)