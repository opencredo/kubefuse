#!/usr/bin/env python

import logging
import sys
import os
import errno
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from cache import ExpiringCache
from client import KubernetesClient
from path import KubePath
from filesystem import KubeFileSystem

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

def main():
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        exit(1)

    logging.basicConfig(level=logging.INFO)
    fuse = FUSE(KubeFuse(sys.argv[1]), sys.argv[1], foreground=True)

if __name__ == '__main__':
    main()
