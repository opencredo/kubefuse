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
        self.fs = KubeFileSystem(self.client)
        self.fd = 0
        print "Mounted on", mount

    def readdir(self, path, fh):
        return self.fs.list_files(KubePath().parse_path(path))

    def getattr(self, path, fh=None):
        return self.fs.getattr(KubePath().parse_path(path))

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return self.fs.read(KubePath().parse_path(path), size, offset)

def main():
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        exit(1)

    logging.basicConfig(level=logging.INFO)
    fuse = FUSE(KubeFuse(sys.argv[1]), sys.argv[1], foreground=True)

if __name__ == '__main__':
    main()
