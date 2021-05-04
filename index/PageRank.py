from __future__ import division
import numpy as np
from scipy.sparse import csr_matrix

class PageRank:
    pagerank_scores = None
    ingoing_edges = None
    outgoing_edges = None
    page_ids = None
    def create_graph(self, ingoing_edges, outgoing_edges, page_ids):
        num_pages = len(page_ids)
        self.pagerank_scores = np.zeros(shape=num_pages)
        self.ingoing_edges = ingoing_edges
        self.outgoing_edges = outgoing_edges
        self.page_ids = page_ids
        # for source_page, target_pages in link_graph.items():
        #     source_page_idx = page_ids[source_page]
        #     for target_page in target_pages:
        #         target_page_idx = page_ids[target_page]
        #         # input for pagerank: adjacency matrix where M_i,j represents the link from 'j' to 'i'
        #         adj_matrix[target_page_idx][source_page_idx] = 1
        #
        # # normalize adj matrix so that sum of column = 1
        # column_sums = adj_matrix.sum(axis=0)
        # self.adj_matrix = adj_matrix / column_sums[np.newaxis, :]

    def load_graph(self):
        pass

    def perform_pagerank(self, num_iterations=100, d=0.85):
        # init values for all pages to 1/N
        num_pages = len(self.pagerank_scores)
        self.pagerank_scores.fill(1 / num_pages)
        for i in range(num_iterations):
            print('Running iteration {} for page rank'.format(i))
            new_page_rank_scores = np.copy(self.pagerank_scores)
            for page_id in self.page_ids:
                page_index = self.page_ids[page_id]
                if page_id in self.ingoing_edges:
                    ingoing_pages = self.ingoing_edges[page_id]
                    sum_score = 0
                    for ingoing_page in ingoing_pages:
                        # can be none if page has no source pages
                        if ingoing_page is not None:
                            ingoing_page_index = self.page_ids[ingoing_page]
                            outgoing_pages = self.outgoing_edges[ingoing_page]
                            # print(len(self.page_ids), ingoing_page_index)
                            page_rank_score = self.pagerank_scores[ingoing_page_index]
                            c = len(outgoing_pages)
                            sum_score += page_rank_score / c
                    new_page_rank_scores[page_index] = (1 - d) + d * sum_score
            self.pagerank_scores = new_page_rank_scores
        print(self.pagerank_scores)


    """PageRank algorithm with explicit number of iterations.
    Source: https://en.wikipedia.org/wiki/PageRank

    Returns
    -------
    ranking of nodes (pages) in the adjacency matrix

    """
    def pagerank(M, num_iterations = 100, d = 0.85):
        """PageRank: The trillion dollar algorithm.

        Parameters
        ----------
        M : numpy array
            adjacency matrix where M_i,j represents the link from 'j' to 'i', such that for all 'j'
            sum(i, M_i,j) = 1
        num_iterations : int, optional
            number of iterations, by default 100
        d : float, optional
            damping factor, by default 0.85

        Returns
        -------
        numpy array
            a vector of ranks such that v_i is the i-th rank from [0, 1],
            v sums to 1

        """
        N = M.shape[1]
        v = np.random.rand(N, 1)
        v = v / np.linalg.norm(v, 1)
        M_hat = (d * M + (1 - d) / N)
        for i in range(num_iterations):
            v = M_hat.dot(v)
        return v

