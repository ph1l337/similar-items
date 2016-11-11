import unittest
import uuid
import tempfile
import os


class TestShingling(unittest.TestCase):

    def test_should_create_shingles_from_single_line_file(self):

        text = "abc def ghi"

        from similaritem import utils

        filepath = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))

        with open(filepath, 'w') as fp:
            fp.write(text)

        shingles = utils.create_shingles_from_file(filepath, 2)

        self.assertEqual(10, len(shingles))
        os.remove(filepath)
