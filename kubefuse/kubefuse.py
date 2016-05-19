#!/usr/bin/env python

import logging
import sys
import os
import errno
from time import time
from stat import S_IFDIR, S_IFLNK, S_IFREG, S_IFIFO
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from cache import ExpiringCache
from client import KubernetesClient
from path import KubePath


        
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
            return self.path.SUPPORTED_ACTIONS
        if self.path.resource_type is not None:
            return client.get_entities(self.path.namespace, self.path.resource_type)
        if self.path.namespace is not None:
            return self.path.SUPPORTED_RESOURCE_TYPES
        return client.get_namespaces() # + ['all']

    def getattr(self, client):
        if not self.path.exists(client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
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
