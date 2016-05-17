import subprocess
import yaml

class KubernetesClient(object):
    def __init__(self):
        self._cache = ExpiringCache(30)

    def _run_command(self, cmd):
        output = subprocess.check_output(['kubectl'] + cmd)
        return yaml.load(output)

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
        payload = self._run_command('get ns -o yaml'.split())
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

    def get_entities(self, ns, entity):
        return self._load_from_cache_or_do(ns + "-" + entity, lambda: self._get_entities(ns,entity))

    def _get_entities(self, ns, entity):
        payload = self._run_command(['get', entity, '-o', 'yaml'] + self._namespace(ns))
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

    def get_object_in_format(self, ns, entity_type, object, format):
        payload = subprocess.check_output(['kubectl', 'get', entity_type, object, '-o', format] + self._namespace(ns))
        return payload

    def describe(self, ns, entity_type, object):
        return subprocess.check_output(['kubectl', 'describe', entity_type, object] + self._namespace(ns))

    def logs(self, ns, object):
        return subprocess.check_output(['kubectl', 'logs', object] + self._namespace(ns))

