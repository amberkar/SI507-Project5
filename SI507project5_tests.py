import unittest
import csv
from SI507project5_code import *


class Proj5(unittest.TestCase):
    def setUp(self):
        self.cache = open('cache_contents.json')
        self.csv1 = open('Tumblr.csv')
        self.csv2 = open('Posts.csv')

    def test_cache(self):
        self.assertTrue(self.cache.read(), 'No cache found')
        self.assertTrue(self.csv1.read(), 'No CSV1 found')
        self.assertTrue(self.csv2.read(), 'No CSV2 found')

    def test_authcreds(self):
        self.assertTrue(self.creds.read(),'No OAuth creds found')

    def test_csv_columns(self):
        self.assertEqual(len(self.csv1.readline().split(',')),4)
        self.assertEqual(len(self.csv2.readline().split(',')),4)

    def test_tags_list(self):
        reader = csv.reader(self.csv1, delimiter=',')
        row1 = next(reader)
        row1 = next(reader)
        self.assertIn('[', row1[3])
        self.assertIn(']', row1[3])

    def test_tumblr_api(self):
        self.assertTrue(type(self.tumblr_test) == type({}), "Testing Tumblr API returns a dictionary.")
        self.assertEqual(len(self.tumblr_test.keys()), 2, "Testing that the dictionary has stuff in it!")

    def test_class_tumblr(self):
        self.assertTrue(self.tumblr_instance.title == "", "Testing Class Tumblr returns data.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
