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


class TestdictToCSVFileRountrip(unittest.TestCase):

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
        keyCol = self.test_header.split('|')[1]
        expected = {
            u'2': {
                u'ett': u'1', u'lista': u'1;2;3;4;5', u'fem': u'5',
                u'tre': u'3', u'tv\xe5': u'2', u'fyra': u'4'},
            u'a2': {
                u'lista': u'a1;a2;a3;a4;a5',
                u'ett': u'a1', u'fem': u'a5', u'tre': u'a3',
                u'tv\xe5': u'a2', u'fyra': u'a4'}}
        result = helpers.csvFileToDict(self.test_infile.name, keyCol,
                                       self.test_header)
        self.assertEquals(result, expected)

    def test_read_list_data(self):
        keyCol = self.test_header.split('|')[1]
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
        result = helpers.csvFileToDict(self.test_infile.name, keyCol,
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
        keyCol = self.test_header.split('|')[1]
        read_data = helpers.csvFileToDict(self.test_infile.name, keyCol,
                                          self.test_header)
        helpers.dictToCsvFile(self.test_outfile.name,
                              read_data, self.test_header)
        self.assertEquals(self.test_outfile.read(), self.test_infile.read())


class TesturldecodeUTF8(unittest.TestCase):

    def test_urldecodeUTF8_on_empty_string_returns_empty_string(self):
        self.assertEquals(helpers.urldecodeUTF8(''), '')

    def test_urldecodeUTF8_iso_string(self):
        input_value = u'http://Prinsessan_Eug%C3%A9nie_av_Sverige_och_Norge'
        expected = u'http://Prinsessan_Eug\xe9nie_av_Sverige_och_Norge'
        self.assertEquals(helpers.urldecodeUTF8(input_value), expected)
