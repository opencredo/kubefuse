from hamcrest import *
import stat
import unittest
from fuse import FuseOSError

from kubefuse.client import KubernetesClient
from kubefuse.path import KubePath
from kubefuse.filesystem import KubeFileSystem

class KubeFileSystemTest(unittest.TestCase):
    def test_getattr_for_namespace(self):
        fs = KubeFileSystem(KubernetesClient())
        path = '/default'
        attr = fs.getattr(path)
        assert_that(attr['st_mode'], is_(stat.S_IFDIR | 0555))
        assert_that(attr['st_nlink'], is_(2))
        assert_that(attr['st_size'], is_(0))
        # NB. time not tested, but whatever

    def test_getattr_for_resource(self):
        fs = KubeFileSystem(KubernetesClient())
        path = '/default/pod'
        attr = fs.getattr(path)
        assert_that(attr['st_mode'], is_(stat.S_IFDIR | 0555))
        assert_that(attr['st_nlink'], is_(2))
        assert_that(attr['st_size'], is_(0))
        # NB. time not tested, but whatever

    def test_getattr_for_object(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        fs = KubeFileSystem(client)
        path = '/default/pod/%s' % pod
        attr = fs.getattr(path)
        assert_that(attr['st_mode'], is_(stat.S_IFDIR | 0555))
        assert_that(attr['st_nlink'], is_(2))
        assert_that(attr['st_size'], is_(0))
        # NB. time not tested, but whatever

    def test_getattr_for_action(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        fs = KubeFileSystem(client)
        path = '/default/pod/%s/describe' % pod
        attr = fs.getattr(path)
        data = client.describe('default', 'pod', pod)
        assert_that(attr['st_mode'], is_(stat.S_IFREG | 0444))
        assert_that(attr['st_nlink'], is_(1))
        assert_that(attr['st_size'], is_(len(data)))
        # NB. time not tested, but whatever

    def test_getattr_size_for_json_action(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        fs = KubeFileSystem(client)
        path = '/default/pod/%s/json' % pod
        attr = fs.getattr(path)
        data = client.get_object_in_format('default', 'pod', pod, 'json')
        assert_that(attr['st_size'], is_(len(data)))

    def test_getattr_size_for_yaml_action(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        fs = KubeFileSystem(client)
        path = '/default/pod/%s/yaml' % pod
        attr = fs.getattr(path)
        data = client.get_object_in_format('default', 'pod', pod, 'yaml')
        assert_that(attr['st_size'], is_(len(data)))

    def test_getattr_size_for_describe_action(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        fs = KubeFileSystem(client)
        path = '/default/pod/%s/logs' % pod
        attr = fs.getattr(path)
        data = client.logs('default', pod)
        assert_that(attr['st_size'], is_(len(data)))

    def test_getattr_for_nonexistent_path(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        path = '/doesnt-exist'
        assert_that(calling(lambda: fs.getattr(path)), raises(FuseOSError))

    def test_getattr_for_truncated_file(self):
        client = KubernetesClient()
        pod = client.get_pods()[0]
        fs = KubeFileSystem(client)
        path = '/default/pod/%s/json' % pod
        fs.truncate(path, 0)
        attr = fs.getattr(path)
        assert_that(attr['st_size'], is_(0))

    def test_list_files_for_root(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        path = '/'
        files = fs.list_files(path)
        namespaces = client.get_namespaces()
        assert_that(files, contains(*namespaces))
        assert_that(len(files), is_(len(namespaces)))

    def test_list_files_for_namespace(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        path = '/default'
        files = fs.list_files(path)
        assert_that(files, contains('pod', 'svc', 'rc', 'nodes', 'events',
            'cs', 'limits', 'pv', 'pvc', 'quota', 'endpoints', 'serviceaccounts',
            'secrets'))

    def test_list_files_for_resource(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        path = '/default/pod'
        files = fs.list_files(path)
        pods = client.get_pods()
        assert_that(files, contains(*pods))

    def test_list_files_for_pod(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s' % pod
        files = fs.list_files(path)
        assert_that(files, has_items('describe', 'logs', 'json', 'yaml'))
        assert_that(len(files), is_(4))

    def test_list_files_for_rc(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        rc = client.get_replication_controllers()[0]
        path = '/default/rc/%s' % rc
        files = fs.list_files(path)
        assert_that(files, has_items('describe', 'json', 'yaml'))
        assert_that(len(files), is_(3))

    def test_list_files_for_file_throws_exception(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/describe' % pod
        assert_that(calling(lambda: fs.list_files(path)), raises(FuseOSError))

    def test_list_files_for_nonexistent_path(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        path = '/doesnt-exist'
        assert_that(calling(lambda: fs.list_files(path)), raises(FuseOSError))

    def test_read_describe(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/describe' % pod
        data = fs.read(path, 50000, 0)
        assert_that(data, equal_to(client.describe('default', 'pod', pod)))

    def test_read_logs(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/logs' % pod
        data = fs.read(path, 50000, 0)
        assert_that(data, equal_to(client.logs('default', pod)))

    def test_read_json(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/json' % pod
        data = fs.read(path, 50000, 0)
        assert_that(data, equal_to(client.get_object_in_format('default', 'pod', pod, 'json')))

    def test_read_yaml(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/yaml' % pod
        data = fs.read(path, 50000, 0)
        assert_that(data, equal_to(client.get_object_in_format('default', 'pod', pod, 'yaml')))

    def test_read_length(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/yaml' % pod
        data = fs.read(path, 10, 0)
        ref = client.get_object_in_format('default', 'pod', pod, 'yaml')
        assert_that(data, equal_to(ref[:10]))

    def test_read_offset(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/yaml' % pod
        data = fs.read(path, 10, 5)
        ref = client.get_object_in_format('default', 'pod', pod, 'yaml')
        assert_that(data, equal_to(ref[5:15]))
        assert_that(len(data), is_(10))

    def test_truncate_and_write(self):
        client = KubernetesClient()
        fs = KubeFileSystem(client)
        pod = client.get_pods()[0]
        path = '/default/pod/%s/yaml' % pod
        fs.truncate(path, 0)
        fs.write(path, 'test', 0)
        fs.write(path, 'write', 4)
        fs.sync(path, dry_run=True)
        data = fs.read(path, 1000, 0)
        assert_that(data, is_('testwrite'))

