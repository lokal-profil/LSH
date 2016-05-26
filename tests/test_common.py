# -*- coding: utf-8  -*-
"""Unit tests for common.py."""

import unittest
from common import (
    Common
)


class TestStdDate(unittest.TestCase):

    """Test the ucfirst method."""

    def test_std_date_on_empty_string_returns_empty_string(self):
        self.assertEquals(Common.std_date(''), '')

    def test_std_date_nd_string_returns_empty_string(self):
        input_value = 'n.d'
        self.assertEquals(Common.std_date(input_value), '')

    def test_std_date_iso_string(self):
        input_value = '1989-02-04'
        expected = '1989-02-04'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_ymd_iso_string(self):
        input_value = '1989-02-04'
        expected = '1989-02-04'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_y_iso_string(self):
        input_value = '1989'
        expected = '1989'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_range_string(self):
        input_value = '1989 - 1990'
        expected = '{{other date|-|1989|1990}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_range_string_no_space(self):
        input_value = '1989-1990'
        expected = '{{other date|-|1989|1990}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_compact_range_string(self):
        input_value = '1989-90'
        expected = '{{other date|-|1989|1990}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_open_range_string_after(self):
        input_value = '1989-'
        expected = '{{other date|>|1989}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_open_range_string_before(self):
        input_value = '-1989'
        expected = '{{other date|<|1989}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_multiple_iso_string(self):
        input_value = '1989-02-04;1984'
        expected = '1989-02-04; 1984'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_decade_string(self):
        input_value = '1980-talet'
        expected = '{{other date|decade|1980}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_century_string(self):
        input_value = '1700-talet'
        expected = '{{other date|century|18}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_start_string(self):
        input_value = u'hösten 1983'
        expected = '{{other date|fall|1983}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_ending_string(self):
        input_value = '1700-talets mitt'
        expected = '{{other date|mid|{{other date|century|18}}}}'
        self.assertEquals(Common.std_date(input_value), expected)

    def test_std_date_modality_string(self):
        input_value = '1989 troligen'
        expected = '1989 {{Probably}}'
        self.assertEquals(Common.std_date(input_value), expected)
