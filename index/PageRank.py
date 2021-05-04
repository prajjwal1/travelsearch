from __future__ import division
import numpy as np
from ElasticSearchIndex import Index
import time

class PageRank:
    def __init__(self, docs):
        inbound_edges = {}
        outbound_edges = {}
        doc_idxs = {}
        # get all page names first
        self.page_names = set([doc['page_name'] for doc in docs])
        self.docs = docs
        for index, doc in enumerate(docs):
            page_name = doc['page_name']
            outbound_edges_for_page = doc['outgoing_edges']
            inbound_edges_for_page = doc['ingoing_edges']
            inbound_edges[page_name] = set(page for page in inbound_edges_for_page if page in self.page_names)
            outbound_edges[page_name] = set(page for page in outbound_edges_for_page if page in self.page_names)
            doc_idxs[page_name] = index
        self.outbound_edges = outbound_edges
        self.inbound_edges = inbound_edges
        self.doc_idxs = doc_idxs
        self.pagerank_scores = None

    def perform_pagerank(self, num_iterations=100, d=0.85):
        self.pagerank_scores = np.zeros(len(self.docs))
        # init values for all pages to 1/N
        num_pages = len(self.pagerank_scores)
        self.pagerank_scores.fill(1 / num_pages)
        for i in range(num_iterations):
            new_page_rank_scores = np.copy(self.pagerank_scores)
            for doc in self.outbound_edges:
                doc_index = self.doc_idxs[doc]
                if doc in self.inbound_edges:
                    ingoing_pages = self.inbound_edges[doc]
                    sum_score = 0
                    for ingoing_page in ingoing_pages:
                        # can be none if page has no source pages
                        if ingoing_page is not None:
                            ingoing_page_index = self.doc_idxs[ingoing_page]
                            outbound_edges = self.outbound_edges[ingoing_page]
                            # print(len(self.page_ids), ingoing_page_index)
                            page_rank_score = self.pagerank_scores[ingoing_page_index]
                            c = len(outbound_edges)
                            sum_score += page_rank_score / c
                    new_page_rank_scores[doc_index] = (1 - d) + d * sum_score
            self.pagerank_scores = new_page_rank_scores
            # want to take the docs with top 10 authority scores
        scores = []
        for index, authority_score in enumerate(self.pagerank_scores):
            scores.append((self.docs[index]['page_name'], authority_score))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return [score[0] for score in scores][0:10]

if __name__ == '__main__':
    start = time.time()
    es = Index()
    res = es.query('japan', 50)
    pr = PageRank(res)
    scores = pr.perform_pagerank()
    print(scores)
    end = time.time()