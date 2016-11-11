import sys
import re
import random


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
    return {(hash(shingle) & maxi) for shingle in shingles}


def create_min_hash_signature(hashed_shingles, hash_funcs):
    signature = [sys.maxsize for _ in range(len(hash_funcs))]
    for shingle_hash in hashed_shingles:
        signature = [min(hfunc(shingle_hash), val) for hfunc, val in zip(hash_funcs, signature)]

    return signature


def generate_signature_functions(n):

    modulus_op = random.randint(2, (1 << 4) - 1)

    hash_funcs = []
    for _ in range(n):
        hash_funcs.append(lambda x: (random.randint(1, 100)*x + random.randint(1, 100)) % modulus_op)

    return hash_funcs
