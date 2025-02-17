import unittest

class TestDefault(unittest.TestCase):
    def test_always_passes(self):
        """This test will always pass."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
