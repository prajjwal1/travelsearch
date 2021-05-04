from util import load_processed_tokens
from InvertedIndex import InvertedIndex

if __name__ == '__main__':
    page_tokens, _, _, _ = load_processed_tokens()
    lemma_index = InvertedIndex(use_lemma=True)
    lemma_index.construct_index(page_tokens)


