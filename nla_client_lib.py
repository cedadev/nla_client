__author__ = 'sjp23'

# Client functions for interacting with CEDA near-line tape archive
#
#


import os
import requests
import json

from nla_client_settings import *

user = os.environ["USER"]
baseurl = NLA_SERVER_URL

def ls(match, stages):
    """return a list of files in nla system given a pattern"""
    url = baseurl + "/api/v1/files?match=%s&stages=%s" % (match, stages)
    response = requests.get(url)
    return response.json()

def make_request(patterns=None, retention=None, files=None, label=None):
    """Add a retrival request into the nla system"""
    url = baseurl + "/api/v1/requests"
    data = {"quota": user}
    assert patterns is None or files is None, "Can't define request files from list and pattern."
    if patterns:
        data["patterns"] = patterns
    if files:
        data["files"] = files
    if retention:
        data["retention"] = retention
    if label:
        data["label"] = label
    response = requests.post(url, data=json.dumps(data))
    return response

def update_request(request_id, retention=None, label=None, notify_first=None, notify_last=None):
    """Add a retrival request into the nla system"""
    url = baseurl + "/api/v1/requests/%s" % request_id
    data = {"quota": user}
    if retention:
        data["retention"] = retention
    if label:
        data["label"] = label
    if notify_first is not None:    # allow null string so that the default email in the user's quota can be used
        data["notify_on_first_file"] = notify_first
    if notify_last is not None:
        data["notify_on_last_file"] = notify_last
    response = requests.put(url, data=json.dumps(data))
    return response

def list_requests():
    """List active retrival requests."""
    url = baseurl + "/api/v1/quota/%s" % user
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def show_request(request_number):
    """show info from a numbered request"""
    url = baseurl + "/api/v1/requests/%s" % request_number
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None




