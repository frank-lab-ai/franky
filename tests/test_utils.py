import unittest
from frank.util import utils


class TestUtils(unittest.TestCase):
    def test_is_number(self):
        self.assertTrue(utils.is_numeric("12.34"))
        self.assertTrue(utils.is_numeric("1234"))
        self.assertTrue(utils.is_numeric("1234748248726347234"))
        self.assertTrue(utils.is_numeric("-1234748248726347234"))
        self.assertTrue(utils.is_numeric("-1234748248726347234e-7"))
        self.assertFalse(utils.is_numeric("some12.34"))

    def test_precision(self):
        self.assertEqual(utils.to_precision(12345, 2), 12000)
        self.assertNotEqual(utils.to_precision(12345, 2), 12300)

    def test_get_number(self):
        self.assertEqual(utils.get_number(12.345, 0.0), 12.345)
        self.assertEqual(utils.get_number(12345, 0.0), 12345)
        self.assertEqual(utils.get_number(-12345, 0.0), -12345)
        self.assertEqual(utils.get_number(123e5, 0.0), 12300000)


if __name__ == '__main__':
    unittest.main()
