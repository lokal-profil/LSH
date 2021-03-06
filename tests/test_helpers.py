#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Test for helper methods
# run from main directory
#
import unittest
import tempfile
import helpers
import os


class TestDictToCSVFileRountrip(unittest.TestCase):

    """Test csvFileToDict() and dictToCsvFile()."""

    def setUp(self):
        # Create a temporary file
        self.test_header = u'ett|två|tre|fyra|fem|lista'
        # the trailing newline reflects that this is added during a write+close
        test_data = u'ett|två|tre|fyra|fem|lista\n' \
                    u'1|2|3|4|5|1;2;3;4;5\n' \
                    u'a1|a2|a3|a4|a5|a1;a2;a3;a4;a5\n'
        self.test_infile = tempfile.NamedTemporaryFile()
        self.test_outfile = tempfile.NamedTemporaryFile(delete=False)
        self.test_infile.write(test_data.encode('utf-8'))
        self.test_infile.seek(0)

    def tearDown(self):
        # Closes and removes the file
        self.test_infile.close()
        os.remove(self.test_outfile.name)

    def test_read_data(self):
        key_col = self.test_header.split('|')[1]
        expected = {
            u'2': {
                u'ett': u'1', u'lista': u'1;2;3;4;5', u'fem': u'5',
                u'tre': u'3', u'tv\xe5': u'2', u'fyra': u'4'},
            u'a2': {
                u'lista': u'a1;a2;a3;a4;a5',
                u'ett': u'a1', u'fem': u'a5', u'tre': u'a3',
                u'tv\xe5': u'a2', u'fyra': u'a4'}}
        result = helpers.csvFileToDict(self.test_infile.name, key_col,
                                       self.test_header)
        self.assertEquals(result, expected)

    def test_read_list_data(self):
        key_col = self.test_header.split('|')[1]
        lists = ('lista', )
        expected = {
            u'2': {
                u'ett': u'1',
                u'lista': [u'1', u'2', u'3', u'4', u'5'],
                u'fem': u'5', u'tre': u'3', u'tv\xe5': u'2', u'fyra': u'4'},
            u'a2': {
                u'lista': [u'a1', u'a2', u'a3', u'a4', u'a5'],
                u'ett': u'a1', u'fem': u'a5', u'tre': u'a3',
                u'tv\xe5': u'a2', u'fyra': u'a4'}}
        result = helpers.csvFileToDict(self.test_infile.name, key_col,
                                       self.test_header, lists=lists)
        self.assertEquals(result, expected)

    def test_write_data(self):
        test_data = {
            u'2': {
                u'ett': u'1', u'lista': u'1;2;3;4;5', u'fem': u'5',
                u'tre': u'3', u'tv\xe5': u'2', u'fyra': u'4'},
            u'a2': {
                u'lista': u'a1;a2;a3;a4;a5',
                u'ett': u'a1', u'fem': u'a5', u'tre': u'a3',
                u'tv\xe5': u'a2', u'fyra': u'a4'}}
        helpers.dictToCsvFile(self.test_outfile.name,
                              test_data, self.test_header)
        self.assertEquals(self.test_outfile.read(), self.test_infile.read())

    def test_write_list_data(self):
        test_data = {
            u'2': {
                u'ett': u'1',
                u'lista': [u'1', u'2', u'3', u'4', u'5'],
                u'fem': u'5', u'tre': u'3', u'tv\xe5': u'2', u'fyra': u'4'},
            u'a2': {
                u'lista': [u'a1', u'a2', u'a3', u'a4', u'a5'],
                u'ett': u'a1', u'fem': u'a5', u'tre': u'a3',
                u'tv\xe5': u'a2', u'fyra': u'a4'}}
        helpers.dictToCsvFile(self.test_outfile.name,
                              test_data, self.test_header)
        self.assertEquals(self.test_outfile.read(), self.test_infile.read())

    def test_read_write_roundtrip(self):
        key_col = self.test_header.split('|')[1]
        read_data = helpers.csvFileToDict(self.test_infile.name, key_col,
                                          self.test_header)
        helpers.dictToCsvFile(self.test_outfile.name,
                              read_data, self.test_header)
        self.assertEquals(self.test_outfile.read(), self.test_infile.read())


class TestUrldecodeUtf8(unittest.TestCase):

    """Test urldecode_utf8()."""

    def test_urldecode_utf8_on_empty_string_returns_empty_string(self):
        self.assertEquals(helpers.urldecode_utf8(''), '')

    def test_urldecode_utf8_plain_string(self):
        input_value = u'http://Prinsessan_Eugenie_av_Sverige_och_Norge'
        expected = u'http://Prinsessan_Eugenie_av_Sverige_och_Norge'
        self.assertEquals(helpers.urldecode_utf8(input_value), expected)

    def test_urldecode_utf8_encoded_string(self):
        input_value = u'http://Prinsessan_Eug%C3%A9nie_av_Sverige_och_Norge'
        expected = u'http://Prinsessan_Eug\xe9nie_av_Sverige_och_Norge'
        self.assertEquals(helpers.urldecode_utf8(input_value), expected)

    def test_urldecode_utf8_encoded_https_string(self):
        input_value = u'https://Prinsessan_Eug%C3%A9nie_av_Sverige_och_Norge'
        expected = u'https://Prinsessan_Eug\xe9nie_av_Sverige_och_Norge'
        self.assertEquals(helpers.urldecode_utf8(input_value), expected)


class TestExternal2internalLink(unittest.TestCase):

    """Test external_2_internal_link()."""

    def test_external_2_internal_link_on_empty_string(self):
        self.assertEquals(helpers.external_2_internal_link(''), '')

    def test_external_2_internal_link_svwiki_string(self):
        input_value = u'http://sv.wikipedia.org/wiki/Some_title'
        expected = u'[[:sv:Some title]]'
        self.assertEquals(helpers.external_2_internal_link(input_value),
                          expected)

    def test_external_2_internal_link_https_svwiki_string(self):
        input_value = u'https://sv.wikipedia.org/wiki/Some_title'
        expected = u'[[:sv:Some title]]'
        self.assertEquals(helpers.external_2_internal_link(input_value),
                          expected)

    def test_external_2_internal_link_non_wiki_url_string(self):
        input_value = u'http://not.a.wiki/Some_title'
        expected = u'http://not.a.wiki/Some_title'
        self.assertEquals(helpers.external_2_internal_link(input_value),
                          expected)

    def test_external_2_internal_link_non_wikipedia_string(self):
        input_value = u'http://se.wikimedia.org/wiki/Some_title'
        expected = u'http://se.wikimedia.org/wiki/Some_title'
        self.assertEquals(helpers.external_2_internal_link(input_value),
                          expected)

    def test_external_2_internal_link_non_wikipedia_string_with_param(self):
        input_value = u'http://commons.wikimedia.org/wiki/Some_title'
        expected = u'[[:commons:Some title]]'
        result = helpers.external_2_internal_link(input_value,
                                                  project='wikimedia')
        self.assertEquals(result, expected)


class TestSplitMultiValuedString(unittest.TestCase):

    """Test split_multi_valued()."""

    def test_split_multi_value_none_gives_none(self):
        self.assertEquals(helpers.split_multi_valued(None),
                          None)

    def test_split_multi_value_empty_gives_empty(self):
        self.assertEquals(helpers.split_multi_valued(''),
                          '')

    def test_split_multi_value_multi_valued_gives_list(self):
        input_value = u'1;2;five'
        expected = [u'1', u'2', u'five']
        self.assertEquals(helpers.split_multi_valued(input_value),
                          expected)

    def test_split_multi_value_different_delimiter(self):
        input_value = u'1|2|five'
        expected = [u'1', u'2', u'five']
        result = helpers.split_multi_valued(input_value, delimiter='|')
        self.assertEquals(result, expected)
