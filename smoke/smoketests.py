#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pysmoke class
"""

from __future__ import print_function
import sys
from multiprocessing.dummy import Pool as ThreadPool
from . import utils
from .testconfig import TestConfig
from .appconfig import AppConfig
from .apicalls import ApiCalls


class SmokeTests(object):
    "Class to run the tests"

    def __init__(self, config_path, tests_path):
        self.tests_config = TestConfig()
        self.app_config = AppConfig(config_path)
        self.api_calls = ApiCalls(
            self.app_config.appurl(),
            self.app_config.vars()
        )
        self.tests_path = tests_path
        self.tests_to_run = {}
        self.verbose = False
        self.filtered_class = ''
        self.single_test = None

    def set_verbose(self, verbose):
        "Set the verbose flag"
        self.verbose = verbose

    def set_filter(self, filtered_class):
        "Set the filtered class to run"
        if filtered_class and ':' in filtered_class:
            parts = filtered_class.split(':')
            self.filtered_class = parts[0]
            self.single_test = parts[1]
        else:
            self.filtered_class = filtered_class

    def run(self):
        "Load and run the tests"
        self.tests_to_run = self.load_tests(self.tests_path)
        errors = self.run_thread(self.tests_to_run)
        self.show_errors(len(self.tests_to_run), errors)

    def load_tests(self, test_path):
        "Load tests from config files"
        tests_to_run = {}
        tests_files = utils.list_files(test_path)
        # just one filtered class
        if self.filtered_class:
            self.tests_config.load(self.tests_path, self.filtered_class)
            return self.compose(self.filtered_class)
        # run all the tests
        for tests_file in tests_files:
            self.tests_config.load(self.tests_path, tests_file)
            tests_to_run.update(self.compose(tests_file))
        return tests_to_run

    def compose(self, filename):
        "Parse config sections"
        tests_to_run = {}
        # if we have a single test
        if self.single_test:
            index = '{0}::{1}::{2}'.format(filename, 0, self.single_test)
            tests_to_run[index] = self.options(
                self.tests_config,
                self.single_test
            )
            return tests_to_run
        # load all sections
        for count, section in enumerate(self.tests_config.sections()):
            index = '{0}::{1}::{2}'.format(filename, count, section)
            tests_to_run[index] = self.options(self.tests_config, section)
        return tests_to_run

    def run_thread(self, tests):
        "Run the tests"
        tests_to_run = sorted(tests.keys())
        pool = ThreadPool(4)
        pool.map(self.run_tests, tests_to_run)
        pool.close()
        pool.join()
        return []
    
    def run_tests(self, key):
        "Run the test"
        print('Running {0} :: {1} \r\n'.format(key, self.tests_to_run[key]))

    @staticmethod
    def options(config, section):
        "Get options"
        options = {}
        for option in config.options(section):
            options[option] = config.get(section, option)
        return options

    @staticmethod
    def show_errors(total_tests, errors):
        "Show error in the console"
        total_errors = len(errors)
        # display errors
        if total_errors > 0:
            print('Executed {0} tests found {1} errors'.format(
                total_tests,
                total_errors
            ))
            for error in errors:
                print('{0}'.format(error))
        # exit program
        if total_errors > 0:
            sys.exit(1)
        sys.exit(0)

    @staticmethod
    def __verbose(method, filename, testname, apiurl, test, response):
        "Print request and response data"
        print('Test: {0} :: {1}'.format(filename, testname))
        print('Endpoint: {0}{1}'.format(apiurl, test['url']))
        print('Method: {0}'.format(method))
        print('Authorization: {0}'.format(test['authorization']))
        print('Payload:')
        print(test['payload'])
        print('Response:')
        for item in response:
            print('{0}: {1}'.format(item, response[item]))
        print('')
