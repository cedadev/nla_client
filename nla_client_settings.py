# NRM 06/12/2016 - set this variable to True to use a test version that uses a local disk
# store as an analogue for the NLA tape system
TEST_VERSION = False

# the baseurl for the api to the nla system

if TEST_VERSION:
    NLA_SERVER_URL = "http://0.0.0.0:8001/nla_control"
else:
    NLA_SERVER_URL = "http://nla.ceda.ac.uk/nla_control"
