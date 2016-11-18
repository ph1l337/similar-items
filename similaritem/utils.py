import hashlib
import random
import re
import sys

L_MAX_32_BIT_INT = ((1 << 31) - 1)


def create_shingles_from_file(filepath, shingle_size):
    shingles = set()
    left_over = ''
    with open(filepath, 'r') as fp:
        for line in fp:
            working_line = left_over + line
            working_line = re.sub('\n', ' ', working_line)
            working_line = re.sub('\t', ' ', working_line)
            working_line = re.sub('[ ]{2,}', ' ', working_line)
            for i in range(len(working_line) - (shingle_size - 1)):
                shingles.add(working_line[i:i + shingle_size])
                left_over = working_line[-(shingle_size - 1):]

    return shingles


def hash_shingles(shingles, maxi):
    return {(chash(shingle) & maxi) for shingle in shingles}


def create_min_hash_signature(hashed_shingles, hash_funcs):
    signature = [sys.maxsize for _ in range(len(hash_funcs))]
    for shingle_hash in hashed_shingles:
        signature = [min(hfunc(shingle_hash), val) for hfunc, val in zip(hash_funcs, signature)]

    return tuple(signature)


def generate_hash_functions(n, hash_buckets):
    hash_funcs = []
    for i in range(n):
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        hash_funcs.append(lambda x, m=a, c=b: (m * x + c) % hash_buckets)

    return hash_funcs


def compute_index_measures(signature_size, threshold, high_recall=True):
    b, r = 2, 1
    n_bands, n_rows = None, None

    while b <= signature_size:

        if r >= signature_size:
            b, r = b + 1, 1

        if b * r == signature_size:
            t = (1.0 / b) ** (1.0 / r)

            if high_recall and t < threshold:
                n_bands, n_rows = b, r  # first pair corresponds to highest r (we don't want it too small)
                break
            elif not high_recall and t > threshold:
                n_bands, n_rows = b, r  # don't break... search for highest b (we don't want it too small)

        r += 1

    return n_bands, n_rows


def create_lsh_candidate_pairs(document_signatures, n_rows, n_bands, hash_buckets):
    import collections

    buckets_in_bands = collections.defaultdict(lambda: collections.defaultdict(list))
    for doc_id, signature in document_signatures.items():
        for band in range(n_bands):
            bucket = chash(signature[band * n_rows:(band + 1) * n_rows]) & hash_buckets
            buckets_in_bands[band][bucket].append(doc_id)

    # memory cost
    # candidates = (candidates for band, bucket in buckets_in_bands.items()
    #               for k, candidates in bucket.items() if len(candidates) > 1)

    candidate_pairs = set()

    for _, band in buckets_in_bands.items():
        for _, bucket in band.items():
            for i in range(len(bucket)):
                for j in range(i + 1, len(bucket)):
                    if bucket[i] < bucket[j]:
                        candidate_pairs.add((bucket[i], bucket[j]))
                    else:
                        candidate_pairs.add((bucket[j], bucket[i]))

    return candidate_pairs


def compute_jaccard_simularity(set1, set2):
    return float(len(set1.intersection(set2))) / len(set1.union(set2))


def check_signature_similarity(candidate_pairs, document_signatures, threshold):
    similar_docs = []
    for candidate_pair in candidate_pairs:
        sig_a = document_signatures[candidate_pair[0]]
        sig_b = document_signatures[candidate_pair[1]]
        sig_len = len(sig_a)
        match_count = sum([1 if sig_a[i] == sig_b[i] else 0 for i in range(0, sig_len)])
        similarity = float(match_count) / sig_len
        if similarity >= threshold:
            similar_docs.append((candidate_pair, similarity))

    return similar_docs


def generate_primes(upper_bound):
    """
    Generates prime numbers until an upper-bound
    for look up ops, sets generally perform better
    but for memory efficiency, we should delete values from the set we no longer need
    and dictionaries seem to fair a little better here

    dict: (~0.07299045276)
    set: (~0.07507979505)
    :param upper_bound:
    :return:
    """
    #
    #

    if upper_bound < 2:
        return

    yield 2

    vals = dict()

    for i in range(3, upper_bound + 1, 2):
        if i not in vals:  # it's marked as true
            yield i
            x = 0
            j = i ** 2 + x * i

            while j < upper_bound:
                vals[j] = False
                x += 1
                j = i ** 2 + x * i
        else:
            del vals[i]


def chash(value):
    """
    Consistent hashing of data for strings and numbers
    :param value: string or numerical value
    :return:
    """

    val = hashlib.sha256(str(value).encode('utf-8')).hexdigest()

    return int(val, 16) & L_MAX_32_BIT_INT
