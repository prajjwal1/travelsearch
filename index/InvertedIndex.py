from collections import Counter
from util import load_stop_words
import os
import operator
import json


class InvertedIndex:
    '''
    index is based on SPIMI
    '''
    def __init__(self, use_lemma):
        self.stop_words = load_stop_words()
        self.index = None
        self.use_lemma = use_lemma
        self.num_docs = 0
        self.terms = None
        # used to save time so we do not have to search the index for a doc when we need to retrieve info like max_tf
        self.doc_to_extra_data_map = {}

    def restore_index(self):
        '''
        Used to restore saved index
        Restore index with terms and postings
        Restore dict that has extra data about documents
        '''
        big_index_dir = 'output/output_final_index'

        extra_index_files = sorted([os.path.join('output', file) for file in os.listdir('output') if 'extra_data' in file])
        self.index, self.doc_to_extra_data_map = self.load_index(big_index_dir, extra_index_files)
        self.num_docs = len(self.doc_to_extra_data_map)
        print(list(self.doc_to_extra_data_map.keys()[0:5]))


    def construct_index(self, doc_tokens):
        block_index = 0
        if not os.path.exists('output'):
            os.mkdir('output')
        if self.use_lemma:
            prefix = 'lemma'
        else:
            prefix = 'stem'
        output_dir = 'output/{}_index_block{}'.format(prefix, block_index)
        index_files = []
        extra_index_files = []
        # inverted index
        output_dict = {}

        # maps all the extra data for all docs in a block
        extra_data_dict = {}
        extra_data_dict_output = 'output/{}_extra_data_block{}'.format(prefix, block_index)

        block_dict = {}
        for index, page in enumerate(doc_tokens):
            tokens = doc_tokens[page]
            print('indexing doc index {}'.format(index))
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
            self.doc_to_extra_data_map[index] = (doc_dict['max_freq'], doc_dict['doc_len'])
            extra_data_dict[index] = doc_dict
            # do block size of 10000 docs
            if (index + 1) % 10000 == 0 or index == len(doc_tokens) - 1:
                # write old block
                self.write_dict(output_dict, output_dir)
                self.write_extra_data(extra_data_dict, extra_data_dict_output)
                index_files.append(output_dir)
                extra_index_files.append(extra_data_dict_output)
                if block_index not in block_dict:
                    block_dict[block_index] = [index]
                else:
                    block_dict[block_index].append(index)
                block_index += 1
                # reset data for next block
                output_dict = {}
                extra_data_dict = {}
                extra_data_dict_output = 'output/{}_extra_data_block{}'.format(prefix, block_index)
                output_dir = 'output/{}_index_block{}'.format(prefix, block_index)
        # merge all the smaller indices into a larger one
        big_index_dir = self.merge_files(index_files)
        self.index, _ = self.load_index(big_index_dir, extra_index_files)

    def load_extra_index(self, extra_index_files):
        with open(extra_index_files[0], 'r') as file:
            extra_index_dict = json.loads(file.read())
        for extra_index_file in extra_index_files[1:]:
            with open(extra_index_file, 'r') as file:
                extra_index_dict.update(json.loads(file.read()))
        return extra_index_dict

    def load_index(self, output_dir, extra_index_files):
        index_dict = {}
        extra_index_dict = self.load_extra_index(extra_index_files)
        with open(output_dir, 'r') as file:
            for line in file:
                line = line.strip().split()
                term = line[0]
                postings = line[1:]
                postings = self.create_postings(term, postings, extra_index_dict)
                index_dict[term] = postings
        self.terms = sorted(index_dict.keys())
        return index_dict, extra_index_dict

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


    def merge_files(self, index_files):
        indices = self.read_file(index_files)
        output_dir = 'output/output_final_index'
        with open(output_dir,'w') as output_file:
            # choose the first file as the master file and merge all of the other files to the master file
            master_file = indices[0]
            text_files = indices[1:]
            for index, text_file in enumerate(text_files):
                master_file = self.merge(master_file, text_file)
            for line in master_file:
                for token in line:
                    output_file.write(str(token) + " ")
                output_file.write('\n')
        return output_dir

    def read_file(self, index_files_dir):
        indices = []
        for index_file_dir in index_files_dir:
            with open(index_file_dir, 'r') as file:
                index = file.read().split('\n')
                processed_index = []
                for line in index:
                    if line != '':
                        line = line.strip().split()
                        parsed_line = []
                        for index in range(len(line)):
                            # convert the document ids to integers
                            if index > 0:
                                parsed_line.append(int(line[index]))
                            else:
                                parsed_line.append(line[index])
                        processed_index.append(parsed_line)
                indices.append(processed_index)
        return indices

    def merge(self, first_file, second_file):
        first_index = 0
        second_index = 0
        combined_file = []
        while first_index < len(first_file) and second_index < len(second_file):
            if first_file[first_index][0] < second_file[second_index][0]:
                combined_file.append(first_file[first_index])
                first_index += 1
            elif first_file[first_index][0] > second_file[second_index][0]:
                combined_file.append(second_file[second_index])
                second_index += 1
            # they are equal so we want to merge
            else:
                first_postings = first_file[first_index][1:]
                second_postings = second_file[second_index][1:]
                term = first_file[first_index][0]
                combined_postings = self.merge_postings(first_postings, second_postings)
                combined_file.append([term] + combined_postings)
                first_index += 1
                second_index += 1
        # there are some left in the first file
        if first_index < len(first_file):
            combined_file.extend(first_file[first_index:])
        # there are some left in the second file
        elif second_index < len(second_file):
            combined_file.extend(second_file[second_index:])

        return combined_file

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




