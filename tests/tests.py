import unittest
import uuid
import tempfile
import os

from similaritem import main
from similaritem import utils


class TestHashing(unittest.TestCase):
    def test_should_hash_shingles(self):

        from similaritem import utils

        shingles = {'ab', 'bc', 'c ', ' d', 'de', 'ef', 'f ', ' g', 'gh', 'hi'}

        for maxi in ((1 << 32) - 1, (1 << 4) - 1, 4):
            hashed_shingles = utils.hash_shingles(shingles, maxi)

            for shingle_hash in hashed_shingles:
                self.assertLessEqual(shingle_hash, maxi)


class TestShingling(unittest.TestCase):
    def test_should_create_shingles_from_single_line_file(self):
        text = "abc def ghi"

        filepath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        with open(filepath, 'w') as fp:
            fp.write(text)

        shingles = utils.create_shingles_from_file(filepath, 2)

        self.assertEqual(10, len(shingles))
        os.remove(filepath)

    def test_should_create_shingles_from_multi_line_file_with_space_around_new_line(self):
        text = 'ghi \n jkl'

        filepath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        with open(filepath, 'w') as fp:
            fp.write(text)

        shingles = utils.create_shingles_from_file(filepath, 2)

        self.assertEqual(6, len(shingles))
        os.remove(filepath)

    def test_should_create_shingles_avoiding_tabs(self):
        text = 'ghi \t jkl'

        filepath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        with open(filepath, 'w') as fp:
            fp.write(text)

        shingles = utils.create_shingles_from_file(filepath, 2)

        self.assertEqual(6, len(shingles))
        os.remove(filepath)

    def test_should_create_shingles_avoiding_empty_line(self):
        text = 'ghi \n                               \n jkl'

        filepath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        with open(filepath, 'w') as fp:
            fp.write(text)

        shingles = utils.create_shingles_from_file(filepath, 2)

        self.assertEqual(6, len(shingles))
        os.remove(filepath)


class TestSignaturing(unittest.TestCase):
    def test_should_create_different_hash_functions(self):
        hash_buckets = 2147483647
        hash_functions = utils.generate_hash_functions(10, hash_buckets)
        for function in hash_functions:
            print(function(5))

    def test_should_create_signature_from_shingles(self):
        hash_funcs = [lambda x: (x + 1) % 5, lambda x: (3 * x + 1) % 5]

        hashed_shingles = [0, 3]
        expected_min_hashing = (1, 0)
        signature = utils.create_min_hash_signature(hashed_shingles, hash_funcs)
        self.assertEqual(2, len(signature))
        self.assertEqual(expected_min_hashing, signature)

        hashed_shingles = [2]
        expected_min_hashing = (3, 2)
        signature = utils.create_min_hash_signature(hashed_shingles, hash_funcs)
        self.assertEqual(2, len(signature))
        self.assertEqual(expected_min_hashing, signature)

        hashed_shingles = [1, 3, 4]
        expected_min_hashing = (0, 0)
        signature = utils.create_min_hash_signature(hashed_shingles, hash_funcs)
        self.assertEqual(2, len(signature))
        self.assertEqual(expected_min_hashing, signature)

        hashed_shingles = [0, 2, 3]
        expected_min_hashing = (1, 0)
        signature = utils.create_min_hash_signature(hashed_shingles, hash_funcs)
        self.assertEqual(2, len(signature))
        self.assertEqual(expected_min_hashing, signature)


class TestLocalitySensitiveHashing(unittest.TestCase):
    def test_should_find_lsh_params_for_high_recall(self):
        signature_size, threshold, high_recall = 50, 0.8, True
        bands, rows = utils.compute_index_measures(signature_size, threshold, high_recall)
        self.assertEqual(10, bands)
        self.assertEqual(5, rows)

    def test_should_find_lsh_params_for_high_precision(self):
        signature_size, threshold, high_recall = 50, 0.8, False
        bands, rows = utils.compute_index_measures(signature_size, threshold, high_recall)
        self.assertEqual(5, bands)
        self.assertEqual(10, rows)

    def test_should_should_create_candidate_pairs(self):
        hash_buckets = 2147483647
        n_bands, n_rows = 2, 5
        document_signatures = {'a': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                               'b': (0, 1, 2, 3, 4, 10, 11, 12, 13, 14),
                               'c': (10, 11, 12, 13, 14, 0, 1, 2, 3, 4)}
        expected_candidates = {('a', 'b')}
        candidates = utils.create_lsh_candidate_pairs(document_signatures, n_rows, n_bands, hash_buckets)
        # TODO implement test that ignores order in tuples
        self.assertSetEqual(expected_candidates, candidates)

    def test_should_find_similar_documents_from_candidate_pairs(self):
        threshold = .8
        document_signatures = {'a': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                               'b': (0, 1, 2, 3, 4, 10, 11, 12, 13, 14),
                               'c': (10, 11, 12, 13, 14, 0, 1, 2, 3, 4),
                               'd': (10, 11, 12, 13, 14, 0, 1, 2, 3, 0)}
        candidates_pairs = {('a', 'b'), ('c', 'd')}
        expected_similar_docs = [(('c', 'd'), 0.9)]
        similar_docs = utils.check_signature_simularity(candidates_pairs, document_signatures, threshold)
        self.assertListEqual(expected_similar_docs, similar_docs)
