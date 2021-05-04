from RankedModel import RankedModel
from InvertedIndex import InvertedIndex
import psutil

if __name__ == '__main__':
    index = InvertedIndex(use_lemma=True)
    index.restore_index()
    model = RankedModel(index)
    model.init_weight_vectors()
    print(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
    vector = model.get_query_vector(['tokyo','drift'], use_w1_scheme=True)
