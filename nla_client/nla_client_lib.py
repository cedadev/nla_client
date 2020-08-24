"""nla_client_lib.py provides a wrapper to calls to the REST-style API which interfaces with the
   CEDA NLA system.  Common calls, such as `ls`, `quota` and making requests are wrapped in a few
   functions."""

__author__ = 'sjp23'

import os
import requests
import json

from nla_client.nla_client_settings import NLA_SERVER_URL

user = os.environ["USER"]
baseurl = NLA_SERVER_URL

def ls(match, stages):
    """.. |br| raw:: html

	       <br />

       Return a list of files in the NLA system given a pattern to match against, and a combination of stages
       of the files to filter on.

       :param string match: A pattern to match filenames against - i.e. does a filename contain this substring
       :param string stages: Filter the files based on the stage of the file within the NLA system.  Stages can be any combination of **UDTAR**

          - **U**: UNVERIFIED
          - **D**: ONDISK
          - **T**: ONTAPE
          - **A**: RESTORING
          - **R**: RESTORED

       :return: A dictionary containing information about the files which match the pattern and stages, consisting of these keys:

                - **count** (*integer*) : The number of files in the NLA system matching the pattern and stage
                - **files** (*List[Dictionary]*]) : A list of information about each file

                |br|

                Each "files" Dictionary can contain the following keys (for each TapeFile):

                - **path** (`string`): logical path to the file.
                - **stage** (`char`): current stage of the file, one of **UDTAR** as above.
                - **verified** (`DateTime`): the date and time the file was verified on.
                - **size** (`integer`): the size of the file in bytes.

       :rtype: Dictionary
       """
    url = baseurl + "/api/v1/files?match=%s&stages=%s" % (match, stages)
    response = requests.get(url)
    return response.json()

def make_request(patterns=None, retention=None, files=None, label=None):
    """Add a retrieval request into the NLA system

       :param string patterns: (`optional`) pattern to match in a logical file path in request to restore files, e.g. "1986" to request to restore all files containing "1986"
       :param DateTime retention: (`optional`) time and date until when the files will remain in the restore area.  Default is 20 days.
       :param List[string] files: (`optional`) list of files to request to restore
       :param string label: (`optional`) user supplied label for the request, visible when user examines their requests

       :return: A HTTP Response object. The two most important elements of this object are:

                    - **status_code** (`integer`): the HTTP status code:

                        - 200 OK: Request was successful
                        - 403 FORBIDDEN: error with user quota: either the user quota is full or the user could not be found

                    - **json()** (`Dictionary`): information about the request, the possible keys are:

                        - **req_id** (`integer`): the unique numeric identifier for the request
                        - **error** (`string`): error message if request fails

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_
       """

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
    """Update an existing retrieval request in the NLA system

       :param integer request_id: the unique integer id of the request
       :param DateTime retention: (`optional`) time and date until when the files will remain in the restore area.  Default is 20 days.
       :param string label: (`optional`) user supplied label for the request, visible when user examines their requests
       :param string notify_first: (`optional`) email address to notify when first restored file is available in the restore area
       :param string notify_last: (`optional`) email address to notify when last file is available in restore area - i.e. the request is complete

       :return: A HTTP Response object. The two most important elements of this object are:

                    - **status_code** (`integer`): the HTTP status code:

                        - 200 OK: Request was successful
                        - 403 FORBIDDEN: error with user quota: the user could not be found
                        - 404 NOT FOUND: the request with `request_id` could not be found

                    - **json()** (`Dictionary`): information about the request, the possible keys are:

                        - **req_id** (`integer`): the unique numeric identifier for the request
                        - **error** (`string`): error message if request fails

       :rtype: `requests.Response <http://docs.python-requests.org/en/master/api/#requests.Response>`_

    """
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
    """List all retrieval requests which have not passed their retention date for the current user.

       :return: A dictionary containing details about the user and the user's requests, consisting of the following keys:

                - **used** (`integer`): the amount of quota the user has used, in bytes
                - **notes** (`string`): any notes about the user - affliations, projects, etc.
                - **email** (`string`): the email address for the user
                - **user** (`string`): the user id of the user - currently their JASMIN login
                - **requests** (`List[Dictionary]`): A list of dictionaries giving information about each request the user has made to the NLA system
                - **id** (`integer`): integer identifier for the user
                - **size** (`integer`): the size of the allocated quota for the current user

                |br|

                Each "requests" Dictionary can contain the following keys (for each TapeRequest):

                - **id** (`integer`): the integer identifier of the request
                - **request_date** (`DateTime`): the date and time the request was made
                - **retention** (`DateTime`): the date and time the request will expire on
                - **label** (`string`): the label assigned to the request by the user, or a default of the request pattern or first file in a listing request
                - **storaged_request_start** (`DateTime`): the date and time the retrieval request started on StorageD
                - **storaged_request_end** (`DateTime`): the date and time the retrieval request concluded on StorageD
                - **first_files_on_disk** (`DateTime`): the date and time the first files arrived on the restore disk
                - **last_files_on_disk** (`DateTime`): the date and time the last files arrived on the restore disk

       :returntype: Dictionary"""
    url = baseurl + "/api/v1/quota/%s" % user
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def show_request(request_number):
    """Show the information for a single request, given the integer identifier of the request.

       :param integer request_number: the unique integer identifier for the request

       :return: A dictionary containing details about the request, consisting of the following keys:

                - **id** (`integer`): unique id of the request
                - **quota** (`string`): the user id for the quota to use in making the request
                - **retention** (`DateTime`): date when restored files will be removed from restore area
                - **request_date** (`DateTime`): date when a request was made
                - **request_patterns** (`string`): pattern to match against to retrieve files from tape
                - **notify_on_first_file** (`string`): email address to notify when first restored file is available in the restore area
                - **notify_on_last_file** (`string`): email address to notify when last file is available in restore area - i.e. the request is complete
                - **label** (`string`): a user defined label for the request
                - **storaged_request_start** (`string`): (*optional*) the date and time the retrieval request started on StorageD
                - **storaged_request_end** (`string`): (*optional*) the date and time the retrieval request concluded on StorageD
                - **first_files_on_disk** (`string`): (*optional*) the date and time the first files arrived on the restore disk
                - **last_files_on_disk** (`string`): (*optional*) the date and time the last files arrived on the restore disk
                - **files** (`List[string]`): list of files in the request

    """
    url = baseurl + "/api/v1/requests/%s" % request_number
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
