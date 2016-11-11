import re
import sys
import os
import os.path
import random
import collections


def usage():
    info = """
    similaritem [-k shingle-size] [-t threshold] path
    Where
        - path: is a path to a file or directory containing text documents
        - k   : is the size of the shingles. Defaults to 9
        - f   : is the threshold for documents signatures, so documents will be considered similar
    """

    print(info)


def main(path, shingle_size=9, threshold=.9):

    files = (os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(file))
    documents_shingles = create_shingles_from_files(files, shingle_size)
    documents_hashes = hash_documents_shingles(documents_shingles)


def hash_documents_shingles(documents):

    maxi = (1 << 32) - 1
    shingles = {}

    for k, shingles in documents.items():
        shingles[k] = [(hash(shingle) & maxi) for shingle in shingles]

    return shingles


#TODO: sort documents hashes
def create_signatures_from_shingles(documents_hashes, signature_size):

    documents_signatures = collections.defaultdict(lambda x: [sys.maxsize for _ in range(signature_size)])
    hash_funcs = generate_signature_functions(signature_size)

    for doc_id, hashes in documents_hashes.items():

        for shingle_hash in hashes[doc_id]:
            signature = [min(hfunc(shingle_hash), val) for hfunc, val in zip(hash_funcs, documents_signatures[doc_id])]
            documents_signatures[doc_id] = signature

    return documents_signatures


def generate_signature_functions(n):

    hash_funcs = []
    for i in range(n):
        hash_funcs.append(lambda x: random.randint(1, 100)*x + random.randint(1, 100))

    return hash_funcs


def create_shingles_from_files(files, shingle_size):

    documents = {}
    for file in files:
        shingles = set()
        left_over = ''
        with open(file, 'r') as f:
            for line in f:
                working_line = left_over + line
                working_line = re.sub('\t', ' ', working_line)
                working_line = re.sub('[ ]{2,}', ' ', working_line)
                for i in range(len(working_line) - shingle_size):
                    shingles.add(working_line[i:i + shingle_size])
                    left_over = working_line[-(shingle_size - 1):]

        documents[file] = shingles

    return documents


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
            shingle_size = int(sys.argv[i+1])

        elif sys.argv[i] == '-t':
            if argc < i + 1:
                usage()
                raise RuntimeError('Missing parameter: -t')

            threshold = float(sys.argv[i+1])
        elif sys.argv[i] == '-path':
            if argc < i + 1:
                usage()
                raise RuntimeError('Missing parameter: -path')

            path = sys.argv[i+1]

            if not os.path.isdir(path):
                usage()
                raise RuntimeError('Path is expected to be a folder with multiple documents')

        else:
            usage()
            raise RuntimeError('Unknown parameter {}'.format(sys.argv[i]))

    main(path, shingle_size, threshold)

if __name__ == '__main__':
    pass


