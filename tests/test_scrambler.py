import unittest
import importlib
import re

# assume we're running from the base project dir:
# python3 tests/test_scrambler.py
spec = importlib.util.spec_from_file_location("scrambler", "./scripts/scrambler.py")
scrambler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scrambler)

class TestScrambler(unittest.TestCase):

    def test_random_name(self):
        result = scrambler.random_name('test.txt')
        self.assertNotEqual(result, "test.txt")
        self.assertEqual(len(result), 14)
        matches = re.findall(r"[a-z0-9]+", result)
        self.assertEqual(len(matches[0]), 10)
        self.assertEqual(len(matches[1]), 3)

    def test_matching_simple(self):
        result = scrambler.matching("./tests/resources", "", "", "")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        self.assertTrue({"file1.txt", "file2.txt", "file2.txt", 
        "file01.java", "file01.ps", "file11.txt"}.issubset(result))
        self.assert_common_excl(result)

    def test_matching_ext(self):
        result = scrambler.matching("./tests/resources", ['java'], "", "")
        self.assert_matching_extention(result)

    def test_matching_ext_dot(self):
        result = scrambler.matching("./tests/resources", ['.java'], "", "")
        self.assert_matching_extention(result)

    def test_matching_substring(self):
        result = scrambler.matching("./tests/resources", "", ["file0"], "")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertFalse({"file1.txt", "file2.txt", "file11.txt"}.issubset(result))
        self.assertTrue({"file01.java", "file01.ps"}.issubset(result))
        self.assert_common_excl(result)

    def test_matching_regex(self):
        result = scrambler.matching("./tests/resources", "", "", "file[0-9]{2}")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertFalse({"file1.txt", "file2.txt", "file11.txt"}.issubset(result))
        self.assertTrue({"file01.java", "file01.ps", "file11.txt"}.issubset(result))
        self.assert_common_excl(result)

    def test_matching_mix(self):
        result = scrambler.matching("./tests/resources", ['txt'], "file", "file[0-9]{2}")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertFalse({"file1.txt", "file2.txt", "file11.txt", "file01.java", "file01.ps"}.issubset(result))
        self.assertTrue({"file11.txt"}.issubset(result))
        self.assert_common_excl(result)

    def assert_common_excl(self, result):
        self.assertFalse("script.py" in result)
        self.assertFalse("script.pyc" in result)
        self.assertFalse("log.log" in result)

    def assert_matching_extention(self, result):
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertFalse({"file1.txt", "file2.txt", "file01.ps", "file11.txt"}.issubset(result))
        self.assertTrue("file01.java" in result)
        self.assert_common_excl(result)

if __name__ == '__main__':
    unittest.main()