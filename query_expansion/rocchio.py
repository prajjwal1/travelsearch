# LIBRARY FOR DATA LOADING
#import xml.etree.ElementTree as ET

# LIBRARY FOR PREPROCESSING
import string
import re
from sklearn.feature_extraction.text import CountVectorizer
import nltk
#nltk.download('corpus')
#from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# LIBRARY FOR RANKED RETRIEVAL
import math, json
from collections import OrderedDict

# PREPROCESSING FUNCTION

#def loadData(location):
    #with open(r'testir5.json') as f:
      #data = json.load(f)
    #return data

def docNumber(location):
    docNo = []
    data = location
    for node in data:
        docNo.append(node["url"])
    return docNo

def docHeadline(location):
    docHead = []
    data = location
    for node in data:
        docHead.append(node[" "])
    return docHead
    
def docText(location):
    docText = []
    data = location
    for node in data:
        docText.append(node["desc"])
    return docText
    
def removePunctuation(textList):
    for i in range(len(textList)):
        for punct in string.punctuation:
            textList[i] = textList[i].replace(punct, " ")
        textList[i] = re.sub(r'^https?:\/\/.*[\r\n]*', '', textList[i], flags=re.MULTILINE)
    return textList

def caseFolding(textList):
    text = []
    for i in range(len(textList)):
        text.append(textList[i].lower())
    return text

def token(sentence):
    token = []
    for word in CountVectorizer().build_tokenizer()(sentence):
        token.append(word)
    return token

def tokenize(textList):
    tokens = []
    for i in range(len(textList)):
        tokens.append(token(textList[i]))
    return tokens

def checkStopword(sentence, stop_words):
    sentence = [w for w in sentence if not w in stop_words]
    return sentence
    
def stopwordRemove(textList):
    #stop_words = set(stopwords.words('english'))
    with open('../query_expansion/stopwords', 'r') as filehandle:
      stop_words = filehandle.read().split()
    text = []
    for i in range(len(textList)):
        text.append(checkStopword(textList[i], stop_words))
    return text

def numberRemove(textList):
    text = []
    for i in range(len(textList)):
        text.append([w for w in textList[i] if not any(j.isdigit() for j in w)])
    return text

def stemming(textList):
    stemmer = PorterStemmer()
    text = textList
    for i in range(len(textList)):
        for j in range(len(textList[i])):
            text[i][j] = stemmer.stem(text[i][j])
    return text

def sorting(textList):
    for i in range(len(textList)):
        textList[i] = sorted(textList[i])
    return textList

def getAllTerms(textList):
    terms = []
    for i in range(len(textList)):
        for j in range(len(textList[i])):
            terms.append(textList[i][j])
    return sorted(set(terms))

# INDEXING FUNCTION

def createIndex(textList, docno):
    terms = getAllTerms(textList)
    proximity = {}
    for term in terms:
        position = {}
        for n in range(len(textList)):
            if(term in textList[n]):
                position[docno[n]] = []
                for i in range(len(textList[n])):
                    if(term == textList[n][i]):
                        position[docno[n]].append(i)
        proximity[term] = position
    return proximity

def exportIndex(index, filename):
    file = open(filename,'w')
    for n in index:
        file.write(n+'\n')
        for o in index[n]:
            file.write('\t'+o+': ')
            for p in range(len(index[n][o])):
                file.write(str(index[n][o][p]))
                if(p<len(index[n][o])-1):
                    file.write(', ')
                else:
                    file.write('\n')
    file.close()
    return "Index's file has been successfully created."


# RANKED RETRIEVAL FUNCTION
def queryInIndex(query, index):
    result = []
    for word in query:
        if word in index:
            result.append(word)
    return result

def df(query, index):
    docFreq = {}
    for word in query:
        if word in index:
            docFreq[word] = len(index[word])
    return docFreq

def idf(df, N):
    inv = {}
    for word in df:
        inv[word] = math.log10(N/df[word])
    return inv

def tf(query, index):
    termFreq = {}
    for word in query:
        freq = {}
        if word in index:
            for i in index[word]:
                freq[i] = len(index[word][i])
        termFreq[word] = freq
    return termFreq

def tfidf(tf, idf):
    w = {}
    for word in tf:
        wtd = {}
        for doc in tf[word]:
            wtd[doc] = (1+(math.log10(tf[word][doc])))*idf[word]
        w[word] = wtd
    return w
    
def score(TFIDF):
    res = {}
    for i in TFIDF:
        for j in TFIDF[i]:
            res[j] = 0
    for i in TFIDF:
        for j in TFIDF[i]:
            res[j] = res[j]+TFIDF[i][j]
    sorted_dict = sorted(res, key=res.get, reverse=True)
    return sorted_dict

def notRelevance(rel, docsNumber):
    notRelevanceNumber = []
    for i in docsNumber:
        if i not in (rel):
            notRelevanceNumber.append(i)
    return notRelevanceNumber

def getIndex(docs, docsNumber):
    res = []
    for i in docs:
        res.append(docsNumber.index(str(i)))
    return res

def vector(text ,terms):
    Vec = []
    for i in range(len(terms)):
        if(terms[i] in text):
            Vec.append(1)
        else:
            Vec.append(0)
    return Vec

def expansion(query, relevan, irrelevan, a, b, c):
    result = {}
    exp    = []
    irrel  = irrelevan[0]
    rel    = relevan[0]
    b      = b / len(relevan)
    c      = c / len(irrelevan)
    
    for i in range(1,len(relevan)):
        for j in range(len(relevan[i])):
            rel[j] = rel[j] + relevan[i][j]
            irrel[j] = irrel[j] + irrelevan[i][j]
            
    for i in range(len(rel)):
        rel[i] = b*rel[i]
        irrel[i] = c*irrel[i]
        query[i] = a*query[i]
        
    for i in range(len(rel)):
        exp.append(query[i]+rel[i]-irrel[i])
        
    for i in range(len(exp)):
        if(exp[i]>0):
            result[i] = exp[i]
        
    return result

def rocchio_main(query, data):
  # LOAD DATA

  #location         = 'testir5.json'
  documentNumber   = docNumber(data)
  #documentHeadline = docHeadline(data)
  documentText     = docText(data)
  documentTotal    = len(documentNumber)
  text             = []


  for i in range(documentTotal):
      text.append(documentText[i])

  # PREPROCESSING
  text = removePunctuation(text)
  text = caseFolding(text)
  text = tokenize(text)
  text = stopwordRemove(text)
  text = numberRemove(text)
  text = stemming(text)


# GET ALL TERMS IN COLLECTION

  terms = getAllTerms(text)

# INDEXING

# index = createIndex(text,documentNumber, terms)
  index = createIndex(text,documentNumber)

  j = []
  j[0] = query
  raw_query = query
# raw_query = newQuery

  query = removePunctuation(raw_query)
  query = caseFolding(query)
  query = tokenize(query)
  query = stopwordRemove(query)
  query = numberRemove(query)
  query = stemming(query)
  query = query[0]

  # Check Query In Index
  query = queryInIndex(query, index)

# RANKED RETRIEVAL

  N               = documentTotal
  tfidf_list      = []

  docFrequency    = df(query, index)
  invDocFrequency = idf(docFrequency, N)
  termFrequency   = tf(query, index)
  TFIDF           = tfidf(termFrequency, invDocFrequency)
  sc              = score(TFIDF)

  relevanceDocNumber = []
  count = 0
  #print('Query: ', raw_query,'\n\n')
  #print('RESULTS: \n')

  for i in range(len(sc)):
      relevanceDocNumber.append(sc[i])
      a = documentNumber.index(sc[i])
  
  # GET NOT RELEVANCE DOC
  notRelevanceNumber = notRelevance(relevanceDocNumber, documentNumber)

# GET DOCUMENT INDEX
  relevanceIndex    = getIndex(relevanceDocNumber,documentNumber)
  notRelevanceIndex = getIndex(notRelevanceNumber,documentNumber)

# CONVERT TO VECTOR
  queryVec      = vector(query, terms)
  relevanVec    = []
  notRelevanVec = []

  for i in relevanceIndex:
      relevanVec.append(vector(text[i], terms))
    
  for i in notRelevanceIndex:
      notRelevanVec.append(vector(text[i], terms))
    
# print(notRelevanVec)

# QUERY EXPANSION VECTOR
  expansionVec = expansion(queryVec, relevanVec, notRelevanVec, 1.0, 0.9, 0.1)

  newQuery = []
  for i in expansionVec:
      newQuery.append(terms[int(i)])
  
  print (newQuery[0:3])
#if __name__ == "__main__":
  #rocchio_main()
