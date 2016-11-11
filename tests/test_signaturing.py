import unittest


class TestSignaturing(unittest.TestCase):

    def test_should_create_signature_from_shingles(self):
        from similaritem import utils

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
