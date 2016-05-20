
class KubePath(object):
    def __init__(self, namespace = None, resource_type = None, object_id = None, action = None):
        self.namespace = namespace 
        self.resource_type = resource_type
        self.object_id = object_id
        self.action = None
        self.SUPPORTED_RESOURCE_TYPES = ['pod', 'svc', 'rc', 'nodes', 'events', 'cs', 'limits', 'pv', 'pvc', 'quota', 'endpoints', 'serviceaccounts', 'secrets']
        self.SUPPORTED_ACTIONS = ['describe', 'json', 'yaml']
        self.SUPPORTED_POD_ACTIONS = ['logs'] + self.SUPPORTED_ACTIONS

    def parse_path(self, path):
        if path == '/': return self
        parts = path[1:].split("/")
        self.namespace = parts[0] if len(parts) > 0 else None
        self.resource_type = parts[1] if len(parts) > 1 else None
        self.object_id = parts[2] if len(parts) > 2 else None
        self.action = parts[3] if len(parts) > 3 else None
        return self

    def exists(self, client):
        if self.namespace is None:
            return True
        namespaces = client.get_namespaces()
        if self.namespace not in namespaces:
            return False
        if self.resource_type is None:
            return True
        if self.resource_type not in self.SUPPORTED_RESOURCE_TYPES:
            return False
        if self.object_id is None:
            return True
        entities = client.get_entities(self.namespace, self.resource_type)
        if self.object_id not in entities:
            return False
        if self.action is None:
            return True
        if self.resource_type == 'pod' and self.action in self.SUPPORTED_POD_ACTIONS:
            return True
        if self.action not in self.SUPPORTED_ACTIONS:
            return False
        return True

    def __repr__(self):
        result = ['<']
        if self.action is not None:
            result.append("action %s on" % self.action)
        if self.object_id is not None:
            result.append('object %s' % self.object_id)
        if self.resource_type is not None:
            result.append("of type %s" % self.resource_type)
        if self.namespace is not None:
            result.append('in namespace %s' % self.namespace)
        result.append('>')
        return " ".join(result)
