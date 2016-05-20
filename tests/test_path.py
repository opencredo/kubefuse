from hamcrest import *
import unittest

from kubefuse.client import KubernetesClient
from kubefuse.path import KubePath

class KubePathTest(unittest.TestCase):
    def test_parse_path_namespace(self):
        kp = KubePath()
        kp.parse_path('/default')
        assert_that(kp.namespace, is_('default'))
        assert_that(kp.resource_type, is_(None))
        assert_that(kp.object_id, is_(None))
        assert_that(kp.action, is_(None))

    def test_parse_path_resource_type(self):
        kp = KubePath()
        kp.parse_path('/default/pod')
        assert_that(kp.namespace, is_('default'))
        assert_that(kp.resource_type, is_('pod'))
        assert_that(kp.object_id, is_(None))
        assert_that(kp.action, is_(None))

    def test_parse_path_object_id(self):
        kp = KubePath()
        kp.parse_path('/default/pod/pod-123')
        assert_that(kp.namespace, is_('default'))
        assert_that(kp.resource_type, is_('pod'))
        assert_that(kp.object_id, is_('pod-123'))
        assert_that(kp.action, is_(None))

    def test_parse_path_action(self):
        kp = KubePath()
        kp.parse_path('/default/pod/pod-123/describe')
        assert_that(kp.namespace, is_('default'))
        assert_that(kp.resource_type, is_('pod'))
        assert_that(kp.object_id, is_('pod-123'))
        assert_that(kp.action, is_('describe'))

    def test_path_exists_pod(self):
        client = KubernetesClient()
        pods = client.get_pods()
        pod1 = pods[0]
        kp = KubePath()
        kp.parse_path('/default/pod/%s/describe' % pod1)
        assert_that(kp.exists(client), is_(True))

    def test_path_exists_svc(self):
        client = KubernetesClient()
        svc = client.get_services()
        svc1 = svc[0]
        kp = KubePath()
        kp.parse_path('/default/svc/%s/describe' % svc1)
        assert_that(kp.exists(client), is_(True))

    def test_path_exists_rc(self):
        client = KubernetesClient()
        rc = client.get_replication_controllers()
        rc1 = rc[0]
        kp = KubePath()
        kp.parse_path('/default/rc/%s/describe' % rc1)
        assert_that(kp.exists(client), is_(True))

    def test_path_exists_invalid_namespace(self):
        client = KubernetesClient()
        kp = KubePath()
        kp.parse_path('/unknown-namespace')
        assert_that(kp.exists(client), is_(False))

    def test_path_exists_invalid_resource(self):
        client = KubernetesClient()
        kp = KubePath()
        kp.parse_path('/default/mylovelyresource')
        assert_that(kp.exists(client), is_(False))

    def test_path_exists_invalid_object_id(self):
        client = KubernetesClient()
        kp = KubePath()
        kp.parse_path('/default/pod/invalid-id')
        assert_that(kp.exists(client), is_(False))

    def test_path_exists_invalid_action(self):
        client = KubernetesClient()
        pods = client.get_pods()
        pod1 = pods[0]
        kp = KubePath()
        kp.parse_path('/default/pod/%s/invalid-action' % pod1)
        assert_that(kp.exists(client), is_(False))
