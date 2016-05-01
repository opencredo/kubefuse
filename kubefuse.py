#!/usr/bin/env python

import logging
import sys
import subprocess
import yaml
from time import time
from stat import S_IFDIR, S_IFLNK, S_IFREG
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

class KubernetesClient(object):
    def _run_command(self, cmd):
        output = subprocess.check_output(['kubectl'] + cmd)
        return yaml.load(output)

    def get_namespaces(self):
        payload = self._run_command('get ns -o yaml'.split())
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

    def get_entities(self, ns, entity):
        payload = self._run_command(['get', entity, '-o', 'yaml', '--namespace', ns])
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

class KubePathBuilder(object):
    def __init__(self, namespace = None, resource_type = None, object_id = None, action = None):
        self.namespace = namespace 
        self.resource_type = resource_type
        self.object_id = object_id
        self.action = None

    def list_files(self, client):
        if self.object_id is not None:
            return ['describe', 'logs', 'json', 'yaml']
        if self.resource_type is not None:
            return client.get_entities(self.namespace, self.resource_type)
        if self.namespace is not None:
            return ['svc', 'pod', 'rc']
        return client.get_namespaces() + ['all']

    def parse_path(self, path):
        if path == '/': return self
        parts = path[1:].split("/")
        self.namespace = parts[0] if len(parts) > 0 else None
        self.resource_type = parts[1] if len(parts) > 1 else None
        self.object_id = parts[2] if len(parts) > 2 else None
        self.action = parts[3] if len(parts) > 3 else None
        print self
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
        
    def _stat_dir(self):
        return dict(st_mode=(S_IFDIR), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def _stat_file(self):
        return dict(st_mode=(S_IFREG), st_nlink=1,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def getattr(self, client):
        if self.action is not None:
            return self._stat_file()
        return self._stat_dir()

class KubeFuse(LoggingMixIn, Operations):

    def __init__(self, kubeconfig, context):
        self.client = KubernetesClient()
        self.path_builder = KubePathBuilder()

    def readdir(self, path, fh):
        return KubePathBuilder().parse_path(path).list_files(self.client)

    def getattr(self, path, fh=None):
        return KubePathBuilder().parse_path(path).getattr(self.client)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: %s <mountpoint> <kubeconfig> <context>' % sys.argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(KubeFuse(sys.argv[2], sys.argv[3]), sys.argv[1], foreground=True)
