from collections import Counter
from util import load_stop_words
import operator
import json
from ElasticSearchIndex import Index
import time

class InvertedIndex:
    '''
    index is based on SPIMI
    '''
    def __init__(self, doc_tokens):
        self.stop_words = load_stop_words()
        self.index = None
        self.num_docs = 0
        self.terms = None
        # used to save time so we do not have to search the index for a doc when we need to retrieve info like max_tf
        self.doc_to_extra_data_map = {}
        self.construct_index(doc_tokens)

    def construct_index(self, doc_tokens):
        # inverted index
        output_dict = {}

        # maps all the extra data for all docs in a block
        extra_data_dict = {}
        for index, page in enumerate(doc_tokens):
            text = page['page_text']
            tokens = [token.lower() for token in text.split()]
            self.num_docs += 1
            filtered_tokens = [token for token in tokens if token not in self.stop_words]
            # self.doc_tokens.append(len(tokens))
            for token in filtered_tokens:
                self.add_to_dict(output_dict, token, index)

            doc_dict = {}
            counter = Counter(filtered_tokens)
            doc_dict['term_freq'] = dict(counter)
            doc_dict['doc_len'] = len(filtered_tokens)
            if len(filtered_tokens) == 0:
                doc_dict['max_freq'] = 0
            else:
                doc_dict['max_freq'] = counter.most_common(1)[0][1]
            extra_data_dict[index] = doc_dict
        self.index = output_dict
        self.doc_to_extra_data_map = extra_data_dict
        self.terms = sorted(self.index.keys())


    def create_postings(self, term, postings, extra_index_dict):
        updated_postings = []
        # create the actual postings by combining data with the extra info
        for doc in postings:
            extra_index_info = extra_index_dict[str(doc)]
            tf = extra_index_info['term_freq'][term]
            max_tf = extra_index_info['max_freq']
            doclen = extra_index_info['doc_len']
            updated_postings.append((doc, tf, max_tf, doclen))
        return updated_postings


    def merge_postings(self, first_postings, second_postings):
        '''
        :param first_postings: list of docs
        :param second_postings: list of docs
        :return: combined list of docs
        '''
        first_index = 0
        second_index = 0
        combined_postings = []
        while first_index < len(first_postings) and second_index < len(second_postings):
            if first_postings[first_index] < second_postings[second_index]:
                combined_postings.append(first_postings[first_index])
                first_index += 1
            elif first_postings[first_index] > second_postings[second_index]:
                combined_postings.append(second_postings[second_index])
                second_index += 1
        # there are some left in the first postings
        if first_index < len(first_postings):
            combined_postings.extend(first_postings[first_index:])
            # there are some left in the second file
        elif second_index < len(second_postings):
            combined_postings.extend(second_postings[second_index:])
        return combined_postings



    def write_dict(self, dict, output_dir):
        # sort terms and then write to output
        sorted_dict = sorted(dict.items(), key=operator.itemgetter(0))
        with open(output_dir, 'w') as file:
            for token, postings in sorted_dict:
                output_str = token + " "
                for doc in postings:
                    output_str += str(doc) + " "
                file.write(output_str + '\n')

    def write_extra_data(self, extra_data_dict, output_dir):
        with open(output_dir, 'w') as file:
            file.write(json.dumps(extra_data_dict))


    def add_to_dict(self, dict, token, doc_num):
        '''
        Add token to dict and return postings list corresponding to token
        :param token: single work token
        :return: postings list
        '''
        if token not in dict:
            dict[token] = [doc_num]
        elif doc_num not in dict[token]:
            dict[token].append(doc_num)



if __name__ == '__main__':
    es = Index()
    res = es.query('vegas')
    start = time.time()
    index = InvertedIndex(res)
    end = time.time()
    print(end-start)
