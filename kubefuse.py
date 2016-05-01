#!/usr/bin/env python

import logging
import sys
import subprocess
import yaml
import os
from time import time
from stat import S_IFDIR, S_IFLNK, S_IFREG, S_IFIFO
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class KubernetesClient(object):
    def _run_command(self, cmd):
        output = subprocess.check_output(['kubectl'] + cmd)
        return yaml.load(output)

    def _namespace(self, ns):
        return ['--namespace', ns] if ns != 'all' else ['--all-namespaces']

    def get_namespaces(self):
        payload = self._run_command('get ns -o yaml'.split())
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

    def get_entities(self, ns, entity):
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


class KubePath(object):
    def __init__(self, namespace = None, resource_type = None, object_id = None, action = None):
        self.namespace = namespace 
        self.resource_type = resource_type
        self.object_id = object_id
        self.action = None

    def parse_path(self, path):
        if path == '/': return self
        parts = path[1:].split("/")
        self.namespace = parts[0] if len(parts) > 0 else None
        self.resource_type = parts[1] if len(parts) > 1 else None
        self.object_id = parts[2] if len(parts) > 2 else None
        self.action = parts[3] if len(parts) > 3 else None
        return self

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
        
class KubeFileSystem(object):
    def __init__(self, path):
        self.path = path

    def _stat_dir(self):
        return dict(st_mode=(S_IFDIR | 0555), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def _stat_file(self):
        return dict(st_mode=(S_IFREG | 0444), st_nlink=1,
                st_size=50000, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def list_files(self, client):
        if self.path.object_id is not None:
            return ['describe', 'logs', 'json', 'yaml']
        if self.path.resource_type is not None:
            return client.get_entities(self.path.namespace, self.path.resource_type)
        if self.path.namespace is not None:
            return ['svc', 'pod', 'rc']
        return client.get_namespaces() # + ['all']

    def getattr(self, client):
        if self.path.action is not None:
            return self._stat_file()
        return self._stat_dir()

    def read(self, client, size, offset):
        if self.path.action is None:
            raise FuseOSError(errno.ENOENT)
        data = ''
        if self.path.action == 'describe':
            data = client.describe(self.path.namespace,
                    self.path.resource_type, self.path.object_id)
        if self.path.action == 'logs':
            data = client.logs(self.path.namespace, self.path.object_id)
        if self.path.action in ['json', 'yaml']:
            data = client.get_object_in_format(self.path.namespace,
                    self.path.resource_type, self.path.object_id, self.path.action)
        return data[offset:size + 1]

class KubeFuse(LoggingMixIn, Operations):

    def __init__(self, mount):
        self.client = KubernetesClient()
        self.fd = 0
	print "Mounted on", mount

    def readdir(self, path, fh):
        return KubeFileSystem(KubePath().parse_path(path)).list_files(self.client)

    def getattr(self, path, fh=None):
        return KubeFileSystem(KubePath().parse_path(path)).getattr(self.client)

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return KubeFileSystem(KubePath().parse_path(path)).read(self.client, size, offset)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        exit(1)

    logging.basicConfig(level=logging.INFO)
    fuse = FUSE(KubeFuse(sys.argv[1]), sys.argv[1], foreground=True)
