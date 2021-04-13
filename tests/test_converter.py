from collections import namedtuple
from unittest import TestCase

from datesense.converter import convert_format

Data = namedtuple("Data", "input expected")


class Test(TestCase):
    def test_convert_format_moment(self):
        test_casts = [
            Data("%Y-%m-%d %H:%m", "YYYY-MM-DD HH:MM")
        ]
        for tc in test_casts:
            self.assertEqual(convert_format(tc.input, "moment"), tc.expected)
