import re


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
    files = (os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path,file)))
    documents_shingles = create_shingles_from_files(files, shingle_size)
    documents_hashes = hash_documents_shingles(documents_shingles)
    jaccard_similarities = compare_sets(documents_hashes)


def hash_documents_shingles(documents):
    maxi = (1 << 32) - 1
    document_hashes = dict()

    for k, shingles in documents.items():
        document_hashes[k] = {(hash(shingle) & maxi) for shingle in shingles}

    return document_hashes


def make_shingle_signatures(documents_shingles):
    for k, shingles in documents_shingles:
        pass


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


def compare_sets(documents_hashes):
    keys = list(documents_hashes.keys())
    pairs = []
    jaccard_similarities = []
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            pairs.append((keys[i], keys[j]))

    for pair in pairs:
        jaccard_similarities.append((pair, calc_jaccard_simularity(documents_hashes[pair[0]], documents_hashes[pair[1]])))

    return jaccard_similarities


def calc_jaccard_simularity(set1, set2):
    return len(set1.intersection(set2)) / len(set1.union(set2))


if __name__ == '__main__':

    import sys
    import os
    import os.path

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

if __name__ == '__main__':
    pass
