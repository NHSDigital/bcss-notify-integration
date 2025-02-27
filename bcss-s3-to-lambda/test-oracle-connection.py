import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_connection_to_oracle(self):
        pass

    def test_get_data_from_oracle(self):
        pass

if __name__ == '__main__':
    unittest.main()
