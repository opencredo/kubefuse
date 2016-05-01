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

    def get_namespaces(self):
        payload = self._run_command('get ns -o yaml'.split())
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

    def get_entities(self, ns, entity):
        namespace = ['--namespace', ns] if ns != 'all' else ['--all-namespaces']
        payload = self._run_command(['get', entity, '-o', 'yaml'] + namespace)
        names = [ item['metadata']['name'] for item in payload['items']]
        return names

    def get_object_in_format(self, ns, entity_type, object, format):
        namespace = ['--namespace', ns] if ns != 'all' else ['--all-namespaces']
        payload = subprocess.check_output(['kubectl', 'get', entity_type, object, '-o', format] + namespace)
        return payload


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
        return dict(st_mode=(S_IFDIR | 0555), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def _stat_file(self):
        return dict(st_mode=(S_IFREG | 0444), st_nlink=1,
                st_size=50000, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def getattr(self, client):
        if self.action is not None:
            return self._stat_file()
        return self._stat_dir()

    def read(self, client, size, offset):
        if self.action is None:
            raise FuseOSError(errno.ENOENT)

        data = ''
        if self.action in ['describe', 'logs']:
            pass
        if self.action in ['json', 'yaml']:
            data = client.get_object_in_format(self.namespace, self.resource_type, self.object_id, self.action)
            data = data[offset:size + 1]
        return data

class KubeFuse(LoggingMixIn, Operations):

    def __init__(self):
        self.client = KubernetesClient()
        self.fd = 0

    def readdir(self, path, fh):
        return KubePathBuilder().parse_path(path).list_files(self.client)

    def getattr(self, path, fh=None):
        return KubePathBuilder().parse_path(path).getattr(self.client)

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return KubePathBuilder().parse_path(path).read(self.client, size, offset)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(KubeFuse(), sys.argv[1], foreground=True)
