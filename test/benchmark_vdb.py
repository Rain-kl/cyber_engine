import random

from rag_core import EmbeddingVectorDB
from tqdm import tqdm


def benchmark_vdb():
    vdb = EmbeddingVectorDB()
    vdb.create('test', 'test_table')
    vdb.add('hello')
    for _ in tqdm(range(1000)):
        alphabet = 'abcdefghijklmnopqrstuvwxyz!@#$%^&*()'
        char = random.choice(alphabet)
        vdb.add(char)
    for _ in tqdm(range(1000)):
        vdb.search('问候')

if __name__ == '__main__':
    benchmark_vdb()