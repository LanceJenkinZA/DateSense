from collections import namedtuple
from unittest import TestCase

import datesense

Data = namedtuple("Data", "input expected")


class TestDateSense(TestCase):
    def test_convert_format_moment(self):
        test_casts = [
            Data(["2002-02-01 15:20"], "%Y-%m-%d %H:%M")
        ]
        for tc in test_casts:
            ds_option = datesense.detect_format(tc.input)
            self.assertEqual(tc.expected, ds_option.get_format_string())
