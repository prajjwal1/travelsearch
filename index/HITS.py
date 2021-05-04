import numpy as np
from ElasticSearchIndex import Index
import time
import requests
from bs4 import BeautifulSoup

class HITS:
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

    def run_hits(self):
        outbound_edges = self.outbound_edges
        inbound_edges = self.inbound_edges

        num_docs = len(outbound_edges)
        authority_scores = np.ones(shape=num_docs)
        hub_scores = np.ones(shape=num_docs)
        num_iterations = 10
        for i in range(num_iterations):
            new_authority_scores = authority_scores.copy()
            new_hub_sores = hub_scores.copy()
            for doc in outbound_edges:
                doc_index = self.doc_idxs[doc]
                outbound_edges_for_doc = outbound_edges[doc]
                inbound_edges_for_doc = inbound_edges[doc]
                for outbound_doc in outbound_edges_for_doc:
                    index = self.doc_idxs[outbound_doc]
                    new_hub_sores[doc_index] += authority_scores[index]
                for inbound_doc in inbound_edges_for_doc:
                    index = self.doc_idxs[inbound_doc]
                    new_authority_scores[doc_index] += hub_scores[index]
            max_authority_score = max(new_authority_scores)
            max_hub_score = max(new_hub_sores)
            authority_scores = new_authority_scores / max_authority_score
            hub_scores = new_hub_sores / max_hub_score
        # want to take the docs with top 10 authority scores
        scores = []
        for index, authority_score in enumerate(authority_scores):
            scores.append((self.docs[index]['page_name'], authority_score))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return [score[0] for score in scores][0:10]

    def get_result(self):
        sites = self.run_hits()
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
    hits = HITS(res)
    print(hits.get_result())
    end = time.time()
    print(end - start)
