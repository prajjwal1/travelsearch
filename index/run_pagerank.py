from util import load_processed_tokens
from PageRank import PageRank

if __name__ == '__main__':
    init_page_rank = True

    if init_page_rank:
        page_tokens, ingoing_edges, outgoing_edges, page_ids = load_processed_tokens()
        page_rank = PageRank()
        page_rank.create_graph(ingoing_edges, outgoing_edges, page_ids)
        page_rank.perform_pagerank()
    else:
        page_rank = PageRank()