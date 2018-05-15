#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pysmoke class
"""

from __future__ import print_function
import sys
from os import listdir
from os.path import isfile
from os.path import join
from smoke.tests import Tests
from smoke.utils import Utils


class SmokeTests(object):
    "Class to run the tests"

    def __init__(self, tests_src, api_calls, verbose):
        "Entry point"
        self.pytest = Tests()
        self.utils = Utils()
        self.tests_src = tests_src
        self.api_calls = api_calls
        self.tests_list = self.list_tests(tests_src)
        self.tests_to_run = {}
        self.verbose = verbose

    @staticmethod
    def list_tests(path):
        "Return a list of test on the folder"
        return [f for f in listdir(path) if isfile(join(path, f))]

    def run(self, config):
        "Load and pysmoke the tests"
        for test_file in self.tests_list:
            config.load(join(self.tests_src, test_file))
            self.compose(config, test_file)
        # pysmoke the tests
        errors = self.run_tests()
        self.show_errors(errors)

    def compose(self, config, filename):
        "Parse config sections"
        count = 0
        for section in config.sections():
            index = '{0}::{1}::{2}'.format(filename, count, section)
            self.tests_to_run[index] = self.options(config, section)
            count += 1
        return None

    @staticmethod
    def options(config, section):
        "Get options"
        options = {}
        count = 0
        for option in config.options(section):
            options[option] = config.get(section, option)
            count += 1
        return options

    def run_tests(self):
        "Run the tests"
        for key in sorted(self.tests_to_run.keys()):
            # display wich test are we running
            index_parts = key.split('::')
            error_index = '{0} :: {1}'.format(index_parts[0], index_parts[2])
            # end display
            test = self.tests_to_run[key]
            tests = self.utils.parse_tests_string(test['tests'])
            response = self.api_calls.call(test)
            # verbose mode
            self.__verbose(
                self.verbose,
                index_parts,
                self.api_calls.get_api_url(),
                test,
                response
            )
            # response = self.utils.get_dummy_response()
            self.pytest.test(response, tests, error_index)
        # the errors
        return self.pytest.get_errors()

    @staticmethod
    def show_errors(errors):
        "Show error in the console"
        for error in errors:
            print(error)
        # exit program
        total_errors = len(errors)
        if total_errors > 0:
            sys.exit(1)
        sys.exit(0)

    @staticmethod
    def __verbose(verbose, key, apiurl, test, response):
        "Print request and response data"
        if verbose:
            print('Test group: {0}'.format(key[0]))
            print('Test name: {0}'.format(key[2]))
            print('API url: {0}'.format(apiurl))
            print('Endpoint: {0}'.format(test['url']))
            print('Authorization: {0}'.format(test['authorization']))
            print('Payload')
            print(test['payload'])
            print('Response')
            for item in response:
                print('{0}: {1}'.format(item, response[item]))
            print('')
