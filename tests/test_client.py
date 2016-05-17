from hamcrest import *
from myna import shim
import unittest

from kubefuse.client import KubernetesClient

tmpdir = None

def setUp():
    global tmpdir
    tmpdir = shim.setup_shim_for('kubectl')	

def tearDown():
    global tmpdir
    if tmpdir is not None:
        shim.teardown_shim_dir(tmpdir)
        tmpdir = None

class KubernetesClientTest(unittest.TestCase):
    def test_get_namespaces(self):
        client = KubernetesClient()
        namespaces = client.get_namespaces()
        assert_that(namespaces, has_item('default'))
        assert_that(namespaces, has_item('kube-system'))
        assert_that(len(namespaces), is_(2))

    def test_get_entities(self):
        pass
    def test_get_object_in_format(self):
        pass
    def test_describe(self):
        pass
    def test_logs(self):
        pass
