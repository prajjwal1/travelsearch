from __future__ import division
from ElasticSearchIndex import Index
from InvertedIndex import InvertedIndex
from math import log10
from util import normalize
import numpy as np
from collections import Counter
import time
import requests
from bs4 import BeautifulSoup


class RankedModel:
    def __init__(self, index):
        self.InvertedIndex = index
        self.doc_vectors = None
        self.num_terms = len(self.InvertedIndex.index)
        self.num_docs = self.InvertedIndex.num_docs
        self.terms = self.InvertedIndex.terms
        self.terms_index = {}
        self.stop_words = index.stop_words
        self.init_weight_vectors()

    def init_weight_vectors(self):
        self.doc_vectors = np.zeros((self.num_terms, self.num_docs))
        for term_index, term_vector in enumerate(self.doc_vectors):
            term = self.terms[term_index]
            self.terms_index[term] = term_index
            for doc_index, weight in enumerate(term_vector):
                tf, max_tf, collection_size, df, doc_len = self.get_stats(term, doc_index)
                # update both vector schemes
                term_vector[doc_index] = self.weighing_scheme1(tf, max_tf, collection_size, df)
            self.doc_vectors[term_index, :] = normalize(term_vector)

    def get_stats(self, term, doc_index):
        postings = self.InvertedIndex.index[term]
        extra_dict = self.InvertedIndex.doc_to_extra_data_map[doc_index]
        max_tf = extra_dict['max_freq']
        term_freq = extra_dict['term_freq']
        if term in term_freq:
            tf = term_freq[term]
        else:
            tf = 0
        doc_len = extra_dict['doc_len']
        df = len(postings)
        collection_size = self.num_docs
        return tf, max_tf, collection_size, df, doc_len

    def get_query_vector(self, query):
        '''
        :param document_index: index of document (0-based)
        :param query: string
        :param use_w1_scheme: configure which scheme to use
        :return: vector associated with the vector
        '''
        vector = np.zeros(shape=self.num_terms)
        tokens = [token for token in query.split() if token not in self.stop_words]
        counter = Counter(tokens)
        for term in tokens:
            if term in self.InvertedIndex.index:
                term_index = self.terms_index[term]
                df = len(self.InvertedIndex.index[term])
                tf = counter[term]
                max_tf = counter.most_common(1)[0][1]
                vector[term_index] = self.weighing_scheme1(tf, max_tf, self.num_docs, df)

        return normalize(vector)

    def weighing_scheme1(self, tf, maxtf, collection_size, df):
        # max term weighting
        return (0.4 + 0.6 * log10(tf + 0.5) / log10(maxtf + 1)) * (log10(collection_size + 0.1 /df) / log10(collection_size))

    def query(self, query, docs):
        query_vector = self.get_query_vector(query)
        doc_vectors = self.doc_vectors
        scores = []
        for index in range(self.num_docs):
            doc_vector = doc_vectors[:, index]
            score = np.dot(doc_vector, query_vector)
            scores.append((index, score))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[0:10]
        return [docs[score[0]]['page_name'] for score in scores][0:10]

    def get_result(self, query, docs):
        sites = self.query(query, docs)
        results = []
        for site in sites:
            result = {}
            result['url'] = site
            html_doc = requests.get(site).text
            soup = BeautifulSoup(html_doc, 'lxml')
            desc = soup.find("meta", property="og:description")['content']
            title = soup.find("meta", property="og:title")['content']
            if len(desc) > 150:
                desc = desc[0:150]
            result['title'] = title
            result['desc'] = desc
            results.append(result)
        return results

if __name__ == '__main__':
    start = time.time()
    es = Index()
    res = es.query('japan')
    index = InvertedIndex(res)
    model = RankedModel(index)
    print(model.get_result('japan', res))
    end = time.time()
    print(end - start)
