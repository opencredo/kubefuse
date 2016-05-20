from hamcrest import *
import yaml
import json
import unittest

from kubefuse.client import KubernetesClient

class KubernetesClientTest(unittest.TestCase):
    def test_get_namespaces(self):
        client = KubernetesClient()
        namespaces = client.get_namespaces()
        assert_that(namespaces, has_item('default'))
        assert_that(namespaces, has_item('kube-system'))
        assert_that(len(namespaces), is_(2))

    def test_get_pods(self):
        client = KubernetesClient()
        pods = client.get_pods('default')
        assert_that(len(pods), is_(3))

    def test_get_services(self):
        client = KubernetesClient()
        svc = client.get_services('default')
        assert_that(len(svc), is_(4))

    def test_get_replication_controllers(self):
        client = KubernetesClient()
        rc = client.get_replication_controllers('default')
        assert_that(len(rc), is_(3))

    def test_get_object_in_yaml_format(self):
        client = KubernetesClient()
        pods = client.get_pods("default")
        pod = client.get_object_in_format('default', 'pod', pods[0], 'yaml')
        result = yaml.load(pod)
        assert_that(result['metadata']['name'], is_(pods[0]))

    def test_get_object_in_json_format(self):
        client = KubernetesClient()
        pods = client.get_pods("default")
        pod = client.get_object_in_format('default', 'pod', pods[0], 'json')
        result = json.loads(pod)
        assert_that(result['metadata']['name'], is_(pods[0]))

    def test_describe(self):
        client = KubernetesClient()
        pods = client.get_pods("default")
        describe = client.describe('default', 'pod', pods[0])
        assert_that(describe, contains_string(pods[0]))

    def test_logs(self):
        client = KubernetesClient()
        pods = client.get_pods("default")
        describe = client.logs('default', pods[0])
        assert_that(describe, contains_string(pods[0]))
