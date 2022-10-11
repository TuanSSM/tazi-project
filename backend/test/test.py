import unittest

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Populate db
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        # Purge db
        print('teardownClass')

    def setUp(self):
        print('setUp')
        #self.
        #self.
        pass

    def tearDown(self):
        print('tearDown\n')
        pass

if __name__ == '__main__':
    unittest.main()
