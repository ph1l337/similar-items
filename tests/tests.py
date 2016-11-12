import unittest
import uuid
import tempfile
import os

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

    def test_should_create_signature_from_shingles(self):

        hash_funcs = [lambda x: (4*x+2) % 5, lambda x: (2*x+3) % 5]

        hashed_shingles = [1, 2, 3, 4, 5]
        expected_min_hashing = [0, 0]
        signature = utils.create_min_hash_signature(hashed_shingles, hash_funcs)
        self.assertEqual(2, len(signature))
        self.assertEqual(expected_min_hashing, signature)

        expected_min_hashing = [0, 1]
        hashed_shingles = [22, 7, 14, 88, 99]
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
