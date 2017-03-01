#! /usr/bin/env python
__author__ = 'sjp23'

# Command line interface to ceda Near line tape (nla)
#
#
#
import cmd
import nla_client_lib
import sys
import datetime
from nla_client_settings import *

class nla_cmd(cmd.Cmd):

    prompt = "NLA>>> "

    def do_ls(self, line):
        """List files in the NLA system.

          Files in the system go through various stages:
          (U) "Unverified" files have been earmarked for tape only archive, but are not yet checked to see if the tape copy is valid.
          (D) "On Disk" files have been verified as having a valid tape copy but have not had the original disk copy deleted.
          (T) "On Tape" files have been removed from disk and only exist as a tape copy.
          (A) "Restoring" files are in the process of Actively being restored to disk.
          (R) "Restored" files are on restoreed to disk. A symlink from the original path points to its tempory location.
                        After the restore request has expired, the disk copy will be removed and the file will be
                        labelled as "On Tape" again.
          (X) "Deleted" If a file is permanantly removed from the archive it is marked as deleted.

          Use the -stage option to list only files at certain stages.  e.g. to list unverified, on disk and on tape files:
             ls -stages=UDT

          The rest of the arguments are a simple contains filter. e.g. for all files with 2015/12/04 in the path:
             ls 2015/12/04
             """
        bits = line.strip().split()
        match = ''
        stages = "UDTAR"

        for b in bits:
            if b[:8] == "-stages=":
                stages = b[8:]
            else:
                match += " " + b
        match = match.strip()

        filelist = nla_client_lib.ls(match, stages)
        files = filelist["files"]
        for f in files:
            print f["path"]

    def do_EOF(self, line):
        """Quit"""
        sys.exit()
    do_quit = do_EOF

    def do_pattern_request(self, line):
        """Request files by matching the pattern string to a substring in the filename"""
        date = datetime.datetime.now() + datetime.timedelta(days=30)
        date = date.strftime("%Y-%m-%d")
        response = nla_client_lib.make_request(patterns=line, retention=date)
        print response
        print response.content

    def do_listing_request(self, line):
        """Make a tape request from a file listing. The file paths should be one per line and absolute."""
        date = datetime.datetime.now() + datetime.timedelta(days=30)
        date = date.strftime("%Y-%m-%d")
        files = open(line).readlines()
        files = map(str.strip, files)
        response = nla_client_lib.make_request(files=files, retention=date)
        print response
        print response.content

    def do_requests(self, line):
        """List requests for current user."""
        quota = nla_client_lib.list_requests()
        print "=== Requests info for %s ===" % quota["user"]
        print "Number of requests: %s" % len(quota["requests"])
        print "Quota size:         %s" % quota["size"]
        print "Total request size: %s" % quota["used"]
        print "Requests:  "
        for req in quota["requests"]:
            print " {id:>6} {label:60}   [{retention}]".format(**req)

    def do_quota(self, line):
        """Check amount of quota remaining"""
        quota = nla_client_lib.list_requests()
        print "=== Quota for %s ===" % quota["user"]
        print "Quota size:         %s" % quota["size"]
        print "Total used:         %s" % quota["used"]
        print "Quota remaining:    %i" % (int(quota["size"]) - int(quota["used"]))

    def emptyline(self):
        pass

    def do_retain(self, line):
        """Set a retention date for a request."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        setresponse = nla_client_lib.update_request(req_id, retention=extra_line)
        print setresponse

    def do_expire(self, line):
        """Set a request as expired by setting the retention date to now."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        setresponse = nla_client_lib.update_request(req_id,
                                                    retention=datetime.datetime.now().strftime("%Y-%m-%d"))
        print setresponse

    def do_notify_first(self, line):
        """Set the email address to notify on the arrival of the first file from tape."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        setresponse = nla_client_lib.update_request(req_id, notify_first=extra_line)
        print setresponse

    def do_notify_last(self, line):
        """Set the email address to notify on the arrival of the last file from tape."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        setresponse = nla_client_lib.update_request(req_id, notify_last=extra_line)
        print setresponse

    def do_notify(self, line):
        """Set the email address to notify for the arrivals of both the first and last file from tape.
    i.e. combine notify_first and notify_last to have the same email address"""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        setresponse = nla_client_lib.update_request(req_id, notify_first=extra_line, notify_last=extra_line)
        print setresponse

    def do_label(self, line):
        """Add a label to a request.
        NLA>>> label 23 John's list of files
        This labels request number 23 "John's list of files"."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        setresponse = nla_client_lib.update_request(req_id, label=extra_line)
        print setresponse

    def do_requested_files(self, line):
        """List the files in a request."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        request_info = nla_client_lib.show_request(req_id)
        for f in request_info["files"]:
            print f

    def show_request(self, line):
        """Show details of a request."""
        req_id, extra_line = self.check_request_id(line)
        if req_id is None:
            return
        request_info = nla_client_lib.show_request(req_id)
        print "=== [%s] ===" % req_id
        if "label" in request_info:
            print "Label:                ", request_info["label"]
        if "request_date" in request_info:
            print "Request date:         ", request_info["request_date"]
        if "retention" in request_info:
            print "Retention:            ", request_info["retention"]
        if "notify_on_first_file" in request_info:
            print "notify_on_first_file: ", request_info["notify_on_first_file"]
        if "notify_on_last_file" in request_info:
            print "notify_on_last_file:  ", request_info["notify_on_last_file"]
        print self.request_status(request_info)

        if "files" in request_info:
            print "%s files in request" % len(request_info["files"])
            for i in range(min(5,len(request_info["files"]))):
                print request_info["files"][i]

    # alias for show_requests
    do_req = show_request

    @staticmethod
    def check_request_id(line):
        """check the first element of a line is a valid request id."""
        bits = line.strip().split()
        if len(bits) == 0:
            print "First argument needs to be a request id."
            return None, None
        try:
            request_number = int(bits[0])
        except ValueError:
            print "%s not a valid request id - they should be integers. " % bits[0]
            return None, None

        # check in request list
        quota = nla_client_lib.list_requests()
        valids = []
        if quota != None:
            for req in quota["requests"]:
                valids.append(req["id"])
        if request_number not in valids:
            print "%s is not a current request number. Valid ids are %s" % (request_number, valids)
            return None, None

        return request_number, " ".join(bits[1:])

    @staticmethod
    def request_status(request_info):
        if "storaged_request_start" not in request_info:
            return "Status: Not queued yet"
        elif "storaged_request_end" not in request_info:
            return "Status: Active (StorageD request started %s)" % request_info["storaged_request_start"]
        else:
            return "Status: On disk (StorageD request ran from %s to %s)" % (request_info["storaged_request_start"],
                                                                        request_info["storaged_request_end"])


if __name__ == "__main__":
    C = nla_cmd()

    # if arguments then just do one command
    if len(sys.argv) > 1:
        C.onecmd(" ".join(sys.argv[1:]))
        sys.exit()

    C.cmdloop("===========================\nCEDA Near line tape utility.\n")
