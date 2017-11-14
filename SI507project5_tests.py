import unittest
import csv
from SI507project5_code import *

class test_cache(unittest.TestCase):
    def setUp(self):
        self.data = open("cache_contents.json",'r')
        self.creds = open("creds.json",'r')

    def test1_cache(self):
        self.assertTrue(self.data.read(), "Ooooops you don't have cached data.")
        self.assertTrue(self.creds.read(), "Oooops you don't have creds data.")

    def tearDown(self):
        self.data.close()
        self.creds.close()

class Data(unittest.TestCase):
    def setUp(self):
        self.tumblr_res_1 = tumblr_res
        self.response = tumblr_result['response'][0]
        self.tags = tumblr_result['response'][0]['tags']

    def test2(self):
        self.assertEqual(type(self.tumblr_res_1),dict,"Testing that tumblr_res_1 successfully returns a dictionary")

    def test3(self):
        self.assertEqual(type(self.response['blog_name']),type(u"s")), "Testing that response is a string"

    def test4(self):
        self.assertEqual(self.tags, ['car','dog','yo yo','water'])

class test_csv_files(unittest.TestCase):
    def setUp(self):
        self.blog = open("Tumblr_Blog.csv",'r')
        self.tags = open("Tumblr_Tags.csv",'r')

    def test5_csv(self):
        self.assertTrue(self.blog.read(), "Oh no, there isn't any data in No data in Tumblr_Blog.csv!")
        self.assertTrue(self.tags.read(), "Oh no, there isn't any data in No data in Tumblr_Tags.csv!")

    def tearDown(self):
        self.blog.close()
        self.tags.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
