import unittest
from frank.kb import conceptnet
# from frank.alist import Alist
# from frank.alist import Attributes as tt


class TestConceptnet(unittest.TestCase):

    def test_findRootWord(self):
        result = conceptnet.find_root_word("sung")
        self.assertTrue("sing" in result)

if __name__ == '__main__':
    unittest.main()
