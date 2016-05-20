from hamcrest import *
import stat
import unittest
from fuse import FuseOSError

from kubefuse.client import KubernetesClient
from kubefuse.path import KubePath
from kubefuse.filesystem import KubeFileSystem

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

    def test_getattr_for_object(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s' % pod)
        fs = KubeFileSystem(path)
        attr = fs.getattr(client)
        assert_that(attr['st_mode'], is_(stat.S_IFDIR | 0555))
        assert_that(attr['st_nlink'], is_(2))
        assert_that(attr['st_size'], is_(0))
        # NB. time not tested, but whatever

    def test_getattr_for_action(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s/describe' % pod)
        fs = KubeFileSystem(path)
        attr = fs.getattr(client)
        assert_that(attr['st_mode'], is_(stat.S_IFREG | 0444))
        assert_that(attr['st_nlink'], is_(1))
        assert_that(attr['st_size'], is_(50000))
        # NB. time not tested, but whatever

    def test_getattr_for_nonexistent_path(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/doesnt-exist')
        fs = KubeFileSystem(path)
        assert_that(calling(lambda: fs.getattr(client)), raises(FuseOSError))

    def test_list_files_for_root(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/')
        fs = KubeFileSystem(path)
        files = fs.list_files(client)
        namespaces = client.get_namespaces()
        assert_that(files, contains(*namespaces))
        assert_that(len(files), is_(len(namespaces)))

    def test_list_files_for_namespace(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/default')
        fs = KubeFileSystem(path)
        files = fs.list_files(client)
        assert_that(files, contains('pod', 'svc', 'rc', 'nodes', 'events',
            'cs', 'limits', 'pv', 'pvc', 'quota', 'endpoints', 'serviceaccounts',
            'secrets'))

    def test_list_files_for_resource(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/default/pod')
        fs = KubeFileSystem(path)
        files = fs.list_files(client)
        pods = client.get_pods()
        assert_that(files, contains(*pods))

    def test_list_files_for_pod(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s' % pod)
        fs = KubeFileSystem(path)
        files = fs.list_files(client)
        assert_that(files, has_items('describe', 'logs', 'json', 'yaml'))
        assert_that(len(files), is_(4))

    def test_list_files_for_rc(self):
        client = KubernetesClient()
        rc = client.get_replication_controllers()[0]
        path = KubePath().parse_path('/default/rc/%s' % rc)
        fs = KubeFileSystem(path)
        files = fs.list_files(client)
        assert_that(files, has_items('describe', 'json', 'yaml'))
        assert_that(len(files), is_(3))

    def test_list_files_for_file_throws_exception(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s/describe' % pod)
        fs = KubeFileSystem(path)
        assert_that(calling(lambda: fs.list_files(client)), raises(FuseOSError))

    def test_list_files_for_nonexistent_path(self):
        client = KubernetesClient()
        path = KubePath().parse_path('/doesnt-exist')
        fs = KubeFileSystem(path)
        assert_that(calling(lambda: fs.list_files(client)), raises(FuseOSError))

    def test_read_describe(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s/describe' % pod)
        fs = KubeFileSystem(path)
        data = fs.read(client, 50000, 0)
        assert_that(data, equal_to(client.describe('default', 'pod', pod)))

    def test_read_logs(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s/logs' % pod)
        fs = KubeFileSystem(path)
        data = fs.read(client, 50000, 0)
        assert_that(data, equal_to(client.logs('default', pod)))

    def test_read_json(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s/json' % pod)
        fs = KubeFileSystem(path)
        data = fs.read(client, 50000, 0)
        assert_that(data, equal_to(client.get_object_in_format('default', 'pod', pod, 'json')))

    def test_read_yaml(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        path = KubePath().parse_path('/default/pod/%s/yaml' % pod)
        fs = KubeFileSystem(path)
        data = fs.read(client, 50000, 0)
        assert_that(data, equal_to(client.get_object_in_format('default', 'pod', pod, 'yaml')))
