from hamcrest import *
from myna import shim
import stat
import unittest

from kubefuse.client import KubernetesClient
from kubefuse.path import KubePath
from kubefuse.filesystem import KubeFileSystem

tmpdir = None

def setUp():
    global tmpdir
    tmpdir = shim.setup_shim_for('kubectl')	

def tearDown():
    global tmpdir
    shim.teardown_shim_dir(tmpdir)

class KubeFileSystemTest(unittest.TestCase):
    def test_getattr_for_namespace(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/default')
        fs = KubeFileSystem(path)
        attr = fs.getattr(client)
        assert_that(attr['st_mode'], is_(stat.S_IFDIR | 0555))
        assert_that(attr['st_nlink'], is_(2))
        assert_that(attr['st_size'], is_(0))
        # NB. time not tested, but whatever

    def test_getattr_for_resource(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/default/pod')
        fs = KubeFileSystem(path)
        attr = fs.getattr(client)
        assert_that(attr['st_mode'], is_(stat.S_IFDIR | 0555))
        assert_that(attr['st_nlink'], is_(2))
        assert_that(attr['st_size'], is_(0))
        # NB. time not tested, but whatever
