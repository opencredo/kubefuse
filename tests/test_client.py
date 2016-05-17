from hamcrest import *
import unittest

from kubefuse.client import KubernetesClient

def setUp():
    # create kubectl shim
    # setup PATH
    print "MODULE SETUP"

def tearDown():
    print "MODULE TEARDOWN"

class KubernetesClientTest(unittest.TestCase):
    def setUp(self):
        print "setup"
    def tearDown(self):
        print "teardown"
    def test_get_namespaces(self):
        pass
    def test_get_entities(self):
        pass
    def test_get_object_in_format(self):
        pass
    def test_describe(self):
        pass
    def test_logs(self):
        pass
