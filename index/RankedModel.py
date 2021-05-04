from __future__ import division
import numpy as np
from math import log10
from collections import Counter
from util import normalize
import numpy as np
from scipy.sparse import csr_matrix

class RankedModel:
    def __init__(self, index):
        self.InvertedIndex = index
        self.vector_scheme1 = None
        self.vector_scheme2 = None
        self.num_terms = len(self.InvertedIndex.index)
        self.num_docs = self.InvertedIndex.num_docs
        self.terms = self.InvertedIndex.terms
        self.terms_index = {}
        self.stop_words = index.stop_words

    def init_weight_vectors(self):
        self.vector_scheme1 = csr_matrix((self.num_terms, self.num_docs))
        for term_index, term_vector in enumerate(self.vector_scheme1):
            term = self.terms[term_index]
            self.terms_index[term] = term_index
            for doc_index, weight in enumerate(term_vector):
                tf, max_tf, collection_size, df, doc_len = self.get_stats(term, doc_index)
                # update both vector schemes
                term_vector[doc_index] = self.weighing_scheme1(tf, max_tf, collection_size, df)
            self.vector_scheme1[term_index] = normalize(term_vector)

    def get_stats(self, term, doc_index):
        postings = self.InvertedIndex.index[term]
        doc_posting = None
        for posting in postings:
            if str(doc_index) == posting[0]:
                doc_posting = posting
                break
        if doc_posting is None:
            tf = 0
            # find max tf if document is not present in postings
            doc_info = self.InvertedIndex.doc_to_extra_data_map[str(doc_index)]
            max_tf = doc_info['max_freq']
            doc_len = doc_info['doc_len']
        else:
            tf = doc_posting[1]
            max_tf = doc_posting[2]
            doc_len = doc_posting[3]
        df = len(postings)
        collection_size = self.num_docs
        return tf, max_tf, collection_size, df, doc_len

    def get_query_vector(self, query, use_w1_scheme):
        '''
        :param document_index: index of document (0-based)
        :param query: list of tokens
        :param use_w1_scheme: configure which scheme to use
        :return: vector associated with the vector
        '''
        vector = np.zeros(shape=self.num_terms)
        counter = Counter(query)
        for term in query:
            if term in self.InvertedIndex.index:
                term_index = self.terms_index[term]
                df = len(self.InvertedIndex.index[term])
                tf = counter[term]
                max_tf = counter.most_common(1)[0][1]
                if use_w1_scheme:
                    vector[term_index] = self.weighing_scheme1(tf, max_tf, self.num_docs, df)

        return normalize(vector)

    def weighing_scheme1(self, tf, maxtf, collection_size, df):
        # max term weighting
        return (0.4 + 0.6 * log10(tf + 0.5) / log10(maxtf + 1)) * (log10(collection_size/df) / log10(collection_size))

    def get_token_vector(self, vector, tokens):
        token_indices = [self.terms_index[token] for token in tokens if token in self.terms_index]
        filtered_vector = np.take(vector, token_indices)
        output_str = ""
        for index, score in enumerate(filtered_vector):
            token_index = token_indices[index]
            output_str += '{}: {} '.format(self.terms[token_index], score)
        return output_str