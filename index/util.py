
import json
from nltk.corpus import stopwords
import nltk
from nltk import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    """"
    Preprocess text to generate tokens by tokenizing and lemmatizing the text using WordNet
    """
    tokens = nltk.word_tokenize(text)
    return [lemmatizer.lemmatize(token.lower()) for token in tokens if token]

def read_json(dir):
    """
    Read json to get tokens and the page links
    """
    # contains tokens for all docs
    page_tokens = {}
    # map page -> other page
    outgoing_edges = {}
    # map other page -> page
    ingoing_edges = {}
    page_ids = {}

    page_index = 0
    with open(dir, 'r') as file:
        pages = json.loads(file.read())
    for page in pages:
        text = page['text']
        source_page = page['url_from']
        # target page has the text
        target_page = page['url_to']

        if source_page not in page_ids:
            page_ids[source_page] = page_index
            page_index += 1

        if target_page not in page_ids:
            page_ids[target_page] = page_index
            page_index += 1

        if target_page not in page_tokens:
            tokens = preprocess(text)
            page_tokens[target_page] = tokens

        if source_page not in outgoing_edges:
            outgoing_edges[source_page] = []
        outgoing_edges[source_page].append(target_page)

        if target_page not in ingoing_edges:
            ingoing_edges[target_page] = []
        ingoing_edges[target_page].append(source_page)

    with open('page_tokens.json', 'w') as file:
        file.write(json.dumps(page_tokens))
    with open('ingoing_edges.json', 'w') as file:
        file.write(json.dumps(ingoing_edges))
    with open('outgoing_edges.json', 'w') as file:
        file.write(json.dumps(outgoing_edges))
    with open('page_ids', 'w') as file:
        file.write(json.dumps(page_ids))

    return page_tokens, ingoing_edges, outgoing_edges, page_ids


def load_processed_tokens():
    with open('page_tokens.json', 'r') as file:
        page_tokens = json.loads(file.read())
    with open('ingoing_edges.json', 'r') as file:
        ingoing_edges = json.loads(file.read())
    with open('outgoing_edges.json', 'r') as file:
        outgoing_edges = json.loads(file.read())
    with open('page_ids', 'r') as file:
        page_ids = json.loads(file.read())

    return page_tokens, ingoing_edges, outgoing_edges, page_ids


def load_stop_words():
    return set(stopwords.words('english'))

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
       return v
    return v / norm
