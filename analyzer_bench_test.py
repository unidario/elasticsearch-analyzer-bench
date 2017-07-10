import unittest
import analyzer_bench
import responses


class TestAnalyzer(unittest.TestCase):
    def test_mean(self):
        """ Calculate the mean number of a list of int/float """
        self.assertEqual(analyzer_bench.calculate_mean([3, 100, 1, 4, 3, 9, 9999, 4]), 1265.375)
        self.assertEqual(analyzer_bench.calculate_mean([9.943, 4.123, 1.39, 5.47]), 5.2315)
        self.assertEqual(analyzer_bench.calculate_mean([3, 100, 1, 4, 3, 9, 9999, 4]), 1265.375)

    def test_col_length(self):
        """
        Calculate the max length of variables treated as strings
        Input: String, various other types (nestled ones as well)
                 Only used inputs are tested
        Structure of test: 3 tests per input combination
          1st test: String has max lenght
          2nd test: Second data structure has max lenght
          3rd test: Length is equal for string and data structure
        """

        # length of string compared to length of int treated as string
        self.assertEqual(analyzer_bench.col_length('Test', 123), 4)
        self.assertEqual(analyzer_bench.col_length('Test', 12345), 5)
        self.assertEqual(analyzer_bench.col_length('Test', 1234), 4)
        # length of string compared to length of strings stored in list
        self.assertEqual(analyzer_bench.col_length('Test', ['a', 'aa', 'aaa', 'b', 'bb']), 4)
        self.assertEqual(analyzer_bench.col_length('Test', ['a', 'aa', 'aaaaa']), 5)
        self.assertEqual(analyzer_bench.col_length('Test', ['aaaa', 'aaa', 'aaa', 'aaaa']), 4)
        # length of string compared to length of int/float treated as strings stroed in dict
        self.assertEqual(
            analyzer_bench.col_length('Test', {'a': 1, 'b': 11, 'c': 2.0, 'f': -12, 'r': 1.1, 0: 231, 5: 222}), 4)
        self.assertEqual(
            analyzer_bench.col_length('Test', {'a': 1.123, 'b': 11, 'c': 2.0, 'f': 153, 'r': 1.1, 0: 231, 5: 222}), 5)
        self.assertEqual(
            analyzer_bench.col_length('Test', {'a': 1, 'b': 11, 'c': 2.0, 'f': 63, 'r': 1.1, 0: 231, 5: 2222}), 4)
        # length of string compared to length of int/float with treated as strings stored in two nested dict with specific key
        self.assertEqual(
            analyzer_bench.col_length('Test', {0: {'a': 123, 0: 123.1}, 1: {'a': -1}, 4: {'b': 1234, 'f': 1.432523}},
                                     'a'), 4)
        self.assertEqual(
            analyzer_bench.col_length('Test', {0: {'a': 123, 0: 123.1}, 1: {'a': -1}, 4: {'b': 1234, 1: 1.432523}}, 1),
            8)
        self.assertEqual(
            analyzer_bench.col_length('Test', {0: {'a': 123, 0: 123.1}, 1: {'a': -1}, 4: {'b': 1234, 'f': 1.432523}},
                                     'b'), 4)
        # length of string compared to length of string with treated as strings stored in three nested dict with specific key
        self.assertEqual(analyzer_bench.col_length('Test', {0: {0: {'a': 'abc', 'b': 'de'}, 1: {'d': 'abcde'}},
                                                            1: {'x': {0: 'abcde', 'f': 'abcd'}}}, 'b'), 4)
        self.assertEqual(analyzer_bench.col_length('Test', {0: {0: {'a': 'abc', 'b': 'de'}, 1: {'d': 'abcde'}},
                                                            1: {'x': {0: 'abcde', 'f': 'abcd'}}}, 'd'), 5)
        self.assertEqual(analyzer_bench.col_length('Test', {0: {0: {'a': 'abc', 'b': 'de'}, 1: {'d': 'abcde'}},
                                                            1: {'x': {0: 'abcde', 'f': 'abcd'}}}, 'f'), 4)


    def test_fetch_metrics(self):
        timing, status, stats = analyzer_bench.fetch_metrics("http://localhost:9200/myindex", "myindex", "myquery")


if __name__ == '__main__':
    unittest.main()
