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
        return self.fs.list_files(path)

    def getattr(self, path, fh=None):
        return self.fs.getattr(path)

    def open(self, path, fh):
        self.fd += 1
        self.fs.open(path, fh)
        return self.fd

    def read(self, path, size, offset, fh):
        return self.fs.read(path, size, offset)

    def truncate(self, path, length, fh=None):
        self.fs.truncate(path, length)
        return 0

    def write(self, path, buf, offset, fh):
        written = self.fs.write(path, buf, offset)
        return written

    def flush(self, path, fh):
        self.fs.sync(path)
        return 0

    def release(self, path, fh):
        self.fs.close(path)
        return 0

def main():
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        exit(1)

    logging.basicConfig(level=logging.INFO)
    fuse = FUSE(KubeFuse(sys.argv[1]), sys.argv[1], foreground=True)

if __name__ == '__main__':
    main()
