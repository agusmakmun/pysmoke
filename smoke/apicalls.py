#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module that make the API calls
"""

import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class ApiCalls(object):
    "Class to make the request to the API"

    def __init__(self, app_url, app_vars, ssl_verify, utils):
        self.app_url = app_url
        self.app_vars = app_vars
        self.utils = utils
        self.ssl_verify = ssl_verify
        self.methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    def call(self, test):
        "Call entry point"
        url = self.app_url + self.utils.vars_replace(
            test["url"], self.app_vars
        )  # noqa:E501
        method = test["method"]
        headers = {}

        if "authorization" in test:
            headers["authorization"] = self.utils.vars_replace(
                test["authorization"], self.app_vars
            )

        payload = self.convert_payload(
            self.utils.vars_replace(test["payload"], self.app_vars)
        )
        # disable warnings
        if self.ssl_verify is False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # make the call
        if method in self.methods:
            if method == "GET":
                response = self.get(url, headers, payload)
            if method == "POST":
                response = self.post(url, headers, payload)
            if method == "PUT":
                response = self.put(url, headers, payload)
            if method == "PATCH":
                response = self.patch(url, headers, payload)
            if method == "DELETE":
                response = self.delete(url, headers, payload)
            # return response
            return {"url": url, "payload": payload, "response": response}
        raise Exception("Error, method not recognized")

    def get(self, url, headers, payload):
        "Make a get call"
        req = requests.get(
            url,
            headers=headers,
            data=payload,
            verify=self.ssl_verify,
        )
        return self.prepare(req)

    def post(self, url, headers, payload):
        "Make a post call"
        req = requests.post(
            url,
            headers=headers,
            data=payload,
            verify=self.ssl_verify,
        )
        return self.prepare(req)

    def put(self, url, headers, payload):
        "Make a put call"
        req = requests.put(
            url,
            headers=headers,
            data=payload,
            verify=self.ssl_verify,
        )
        return self.prepare(req)

    def patch(self, url, headers, payload):
        "Make a patch call"
        req = requests.patch(
            url,
            headers=headers,
            data=payload,
            verify=self.ssl_verify,
        )
        return self.prepare(req)

    def delete(self, url, headers, payload):
        "Make a get call"
        req = requests.delete(
            url,
            headers=headers,
            data=payload,
            verify=self.ssl_verify,
        )
        return self.prepare(req)

    def get_api_url(self):
        "Get the API url"
        return self.app_url

    @staticmethod
    def convert_payload(payload):
        "Try to convert payload to object or leave it"
        try:
            return json.loads(payload)
        except ValueError:
            return payload

    @staticmethod
    def prepare(request):
        "Object with the request result"
        return {
            "http_status": request.status_code,
            "headers": request.headers,
            "response": request.json(),
            "elapsed_time": request.elapsed.total_seconds(),
        }
