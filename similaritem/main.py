import collections
import os
import os.path
import random
import sys

from . import utils

random.seed(1786)
HASH_BUCKETS = 2147483647  # largest 32bit unsigned-integer prime


def usage():
    info = """
    similaritem [-k shingle-size] [-t threshold] path
    Where
        - path: is a path to a file or directory containing text documents
        - k   : is the size of the shingles. Defaults to 9
        - t   : is the threshold for documents signatures, so documents will be considered similar. Defaults to .8
    """

    print(info)


def main(path, shingle_size=9, threshold=.8, signature_size=100):
    files = (os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))
    documents_shingles = create_shingles_from_files(files, shingle_size)
    documents_shingles_hashes = hash_documents_shingles(documents_shingles, HASH_BUCKETS)
    jaccard_similarities = compare_sets(documents_shingles_hashes)
    print('The following jaccard similiarities between the k={k} k-shingles of all pairs of documents were found:\n'
          .format(k=shingle_size) +
          '\n'.join('{doc_a} \t - {doc_b}: \t {jaccard_sim}'
                      .format(doc_a=pair[0][0], doc_b=pair[0][1], jaccard_sim=pair[1]) for pair in
                      jaccard_similarities))

    document_signatures = create_signatures_from_shingles(documents_shingles_hashes, signature_size)
    n_bands, n_rows = utils.compute_index_measures(signature_size, threshold)
    similar_docs = find_similar_docs_using_lsh(document_signatures, n_rows, n_bands, threshold)
    print('Using LSH with a threshold of {t} the following document pairs were found to be similar:\n'
          .format(t=threshold) +
          '\n'.join('{doc_a} \t - {doc_b}'.format(doc_a=pair[0], doc_b=pair[1]) for pair in similar_docs))


def hash_documents_shingles(documents, hash_buckets):
    document_hashes = dict()

    for k, shingles in documents.items():
        document_hashes[k] = utils.hash_shingles(shingles, hash_buckets)

    return document_hashes


# TODO: sort documents hashes - why? I think there's no need
def create_signatures_from_shingles(documents_hashes, signature_size):
    documents_signatures = {}
    min_hash_funcs = utils.generate_hash_functions(signature_size, HASH_BUCKETS)

    for doc_id, doc_shingle_hashes in documents_hashes.items():
        documents_signatures[doc_id] = utils.create_min_hash_signature(doc_shingle_hashes, min_hash_funcs)

    return documents_signatures


def create_shingles_from_files(files, shingle_size):
    documents = {}
    for file in files:
        documents[file] = utils.create_shingles_from_file(file, shingle_size)

    return documents


def compare_sets(documents_hashes):
    keys = list(documents_hashes.keys())
    pairs = []
    jaccard_similarities = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            pairs.append((keys[i], keys[j]))

    for pair in pairs:
        jaccard_similarities.append(
            (pair, compute_jaccard_simularity(documents_hashes[pair[0]], documents_hashes[pair[1]])))

    return jaccard_similarities


def compute_jaccard_simularity(set1, set2):
    return float(len(set1.intersection(set2))) / len(set1.union(set2))


def find_similar_docs_using_lsh(document_signatures, n_rows, n_bands, threshold):
    candidate_pairs = utils.create_lsh_candidate_pairs(document_signatures, n_rows=n_rows, n_bands=n_bands,
                                                       hash_buckets=HASH_BUCKETS)
    similar_docs = utils.check_signature_simularity(candidate_pairs, document_signatures, threshold)

    return similar_docs


if __name__ == '__main__':

    argc = len(sys.argv)
    if argc < 3:
        usage()
        sys.exit(1)

    path = None
    shingle_size = False
    threshold = None
    path = None

    for i in range(1, argc, 2):
        if sys.argv[i] == '-k':
            if argc < i + 1:
                usage()
                raise RuntimeError('Missing parameter: -k')
            shingle_size = int(sys.argv[i + 1])

        elif sys.argv[i] == '-t':
            if argc < i + 1:
                usage()
                raise RuntimeError('Missing parameter: -t')

            threshold = float(sys.argv[i + 1])
        elif sys.argv[i] == '-path':
            if argc < i + 1:
                usage()
                raise RuntimeError('Missing parameter: -path')

            path = sys.argv[i + 1]

            if not os.path.isdir(path):
                usage()
                raise RuntimeError('Path is expected to be a folder with multiple documents')

        else:
            usage()
            raise RuntimeError('Unknown parameter {}'.format(sys.argv[i]))

    main(path, shingle_size, threshold)
