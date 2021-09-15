import subprocess
import yaml
import tempfile
import six

import cache


class KubernetesClient(object):
    def __init__(self, kubeconfig=None, cluster=None, context=None, user=None):
        self._cache = cache.ExpiringCache(30)
        self.kubeconfig = kubeconfig
        self.cluster = cluster 
        self.context = context
        self.user = user

    def _base_kubectl_command(self):
        result = ['kubectl']
        if self.kubeconfig is not None:
            result += ['--kubeconfig', self.kubeconfig]
        if self.cluster is not None:
            result += ['--cluster', self.cluster]
        if self.context is not None:
            result += ['--context', self.context]
        if self.user is not None:
            result += ['--user', self.user]
        return result

    def _run_command(self, cmd):
        return subprocess.check_output(' '.join(self._base_kubectl_command() + cmd), shell=True)

    def _run_command_and_parse_yaml(self, cmd):
        return yaml.load(self._run_command(cmd))

    @staticmethod
    def _namespace(ns):
        return ['--namespace', ns] if ns != 'all' else ['--all-namespaces']

    def _load_from_cache_or_do(self, key, func):
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        result = func()
        self._cache.set(key, result)
        return result
        
    def get_namespaces(self):
        key = "namespaces"
        cb = self._get_namespaces
        return self._load_from_cache_or_do(key, cb)

    def get_entities(self, ns, entity):
        key = "%s.%s" % (ns, entity)
        cb = lambda: self._get_entities(ns, entity)
        return self._load_from_cache_or_do(key, cb)

    def get_object_in_format(self, ns, entity_type, object, format):
        key = "%s.%s.%s.%s" % (ns, entity_type, object, format)
        cb = lambda: self._get_object_in_format(ns, entity_type, object, format)
        return self._load_from_cache_or_do(key, cb)

    def describe(self, ns, entity_type, object):
        key = "%s.%s.%s.describe" % (ns, entity_type, object)
        cb = lambda: self._describe(ns, entity_type, object)
        return self._load_from_cache_or_do(key, cb)

    def delete_from_cache(self, ns, entity_type, object, format):
        key = "%s.%s.%s.%s" % (ns, entity_type, object, format)
        self._cache.delete(key)

    def logs(self, ns, object):
        key = "%s.pod.%s.logs" % (ns, object)
        cb = lambda: self._logs(ns, object)
        return self._load_from_cache_or_do(key, cb)

    def get_pods(self, ns='default'):
        return self.get_entities(ns, 'pod')
    def get_services(self, ns='default'):
        return self.get_entities(ns, 'svc')
    def get_replication_controllers(self, ns='default'):
        return self.get_entities(ns, 'rc')

    def replace(self, data):
        tmpfile = tempfile.mktemp()
        with open(tmpfile, 'w') as f:
            f.write(data)
        six.print_(self._run_command(('apply -f ' + tmpfile).split()))


    def _get_namespaces(self):
        payload = self._run_command_and_parse_yaml('get ns -o yaml'.split())
        if payload is None or 'items' not in payload:
            return []
        return [item['metadata']['name'] for item in payload['items']]

    def _get_entities(self, ns, entity):
        payload = self._run_command_and_parse_yaml(['get', entity, '-o', 'yaml'] + self._namespace(ns))
        if payload is None or 'items' not in payload:
            return []
        return [item['metadata']['name'] for item in payload['items']]

    def _get_object_in_format(self, ns, entity_type, object, format):
        return self._run_command(['get', entity_type, object, '-o', format] + self._namespace(ns))

    def _describe(self, ns, entity_type, object):
        return self._run_command(['describe', entity_type, object] + self._namespace(ns))

    def _logs(self, ns, object):
        return self._run_command(['logs', object] + self._namespace(ns))

