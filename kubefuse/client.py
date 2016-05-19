import subprocess
import yaml

from cache import ExpiringCache

class KubernetesClient(object):
    def __init__(self):
        self._cache = ExpiringCache(30)

    def _run_command(self, cmd):
        return subprocess.check_output(' '.join(['kubectl'] + cmd), shell=True)

    def _run_command_and_parse_yaml(self, cmd):
        return yaml.load(self._run_command(cmd))

    def _namespace(self, ns):
        return ['--namespace', ns] if ns != 'all' else ['--all-namespaces']

    def _load_from_cache_or_do(self, key, func):
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        result = func()
        self._cache.set(key, result)
        return result
        
    def get_namespaces(self):
        return self._load_from_cache_or_do("namespaces", self._get_namespaces)

    def _get_namespaces(self):
        payload = self._run_command_and_parse_yaml('get ns -o yaml'.split())
        if payload is None or 'items' not in payload:
            return []
        return [ item['metadata']['name'] for item in payload['items']]

    def get_pods(self, ns='default'):
        return self.get_entities(ns, 'pod')
    def get_services(self, ns='default'):
        return self.get_entities(ns, 'svc')
    def get_replication_controllers(self, ns='default'):
        return self.get_entities(ns, 'rc')

    def get_entities(self, ns, entity):
        return self._load_from_cache_or_do(ns + "-" + entity, 
                lambda: self._get_entities(ns,entity))

    def _get_entities(self, ns, entity):
        payload = self._run_command_and_parse_yaml(['get', entity, '-o', 'yaml'] + self._namespace(ns))
        if payload is None or 'items' not in payload:
            return []
        return [ item['metadata']['name'] for item in payload['items']]

    def get_object_in_format(self, ns, entity_type, object, format):
        return self._run_command(['get', entity_type, object, '-o', format] + self._namespace(ns))

    def describe(self, ns, entity_type, object):
        return self._run_command(['describe', entity_type, object] + self._namespace(ns))

    def logs(self, ns, object):
        return self._run_command(['logs', object] + self._namespace(ns))

