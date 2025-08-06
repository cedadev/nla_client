"""Settings for the NLA system, mostly controlling whether the test version or production version is used."""


#: set this variable to True to use a test version that uses a local disk
#: store as an analogue for the NLA tape system
TEST_VERSION = False

if TEST_VERSION:
    #: the baseurl for the api to the NLA system
    NLA_SERVER_URL = "http://0.0.0.0:8001/nla_control"
else:
    NLA_SERVER_URL = "http://nla.ceda.ac.uk/nla_control"

VERIFY_CERT = False