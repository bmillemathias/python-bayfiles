import os
import sys
import unittest
import hashlib

sys.path.append('..')

import bayfiles

class TestFile(unittest.TestCase):

    def __get_sha1hash(self, filepath):
        """Return the sha1 hash on the entire content of the file passed."""

        # Don't know if it's "right" to import a module in a function
        import hashlib

        sha1_obj = hashlib.sha1()
        with open(filepath, 'rb') as file_r:
            while True:
                buffr = file_r.read(0x100000)
                if not buffr:
                    break
                sha1_obj.update(buffr)

        sha1hash = sha1_obj.hexdigest()
        return sha1hash

    def test_sha1(self):
        sha1hash = self.__get_sha1hash(os.path.realpath(__file__))
        f = bayfiles.File(os.path.realpath(__file__))
        f.upload()
        self.assertEqual(sha1hash.__str__,f.metadata[u'sha1'])


if __name__ == '__main__':
    unittest.main()
