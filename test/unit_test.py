import os
import sys
import unittest
import hashlib
import exceptions

# Add parent to sys path to be able to import bayfiles
sys.path.append('..')

import bayfiles

class TestFile(unittest.TestCase):

    def __get_sha1hash(self, filepath):
        """Return the sha1 hash on the entire content of the file passed."""

        sha1_obj = hashlib.sha1()
        with open(filepath, 'rb') as file_r:
            while True:
                buffr = file_r.read(0x100000)
                if not buffr:
                    break
                sha1_obj.update(buffr)

        sha1hash = sha1_obj.hexdigest()
        return sha1hash

    def test_anon_upload(self):
        """Test the anonymous upload."""
        sha1hash = self.__get_sha1hash(os.path.realpath(__file__))
        f = bayfiles.File(os.path.realpath(__file__))
        f.upload()
        self.assertEqual(sha1hash,f.metadata[u'sha1'])

    def test_account_missing_args(self):
        """test an exception is raised if no arguments are passed."""
        self.assertRaises(exceptions.Exception, bayfiles.Account)


if __name__ == '__main__':
    unittest.main()
