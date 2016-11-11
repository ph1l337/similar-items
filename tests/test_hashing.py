import unittest


class TestHashing(unittest.TestCase):

    def test_should_hash_shingles(self):

        from similaritem import utils

        shingles = {'ab', 'bc', 'c ', ' d', 'de', 'ef', 'f ', ' g', 'gh', 'hi'}

        for maxi in ((1 << 32) - 1, (1 << 4) - 1, 4):
            hashed_shingles = utils.hash_shingles(shingles, maxi)

            for shingle_hash in hashed_shingles:
                self.assertLessEqual(shingle_hash, maxi)
