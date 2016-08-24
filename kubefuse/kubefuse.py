#!/usr/bin/env python

import logging
import sys
import os
import errno
import six
import argparse
import sys
try:
    from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
except EnvironmentError:
    print "It looks like the Fuse system library is missing."
    print "Please install libfuse using your OS's package manager, or download OSXFUSE if you're on a Mac"
    sys.exit(1)


from . import client
from . import filesystem 

class KubeFuse(LoggingMixIn, Operations):

    def __init__(self, mount, kubeconfig = None, cluster = None, context = None, user = None):
        self.client = client.KubernetesClient(kubeconfig, cluster, context, user)
        self.fs = filesystem.KubeFileSystem(self.client)
        self.fd = 0
        six.print_("Mounting KubeFuse on", mount)

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

def parse_args():
    parser = argparse.ArgumentParser(description='A file system view for Kubernetes')
    parser.add_argument('mountpoint', metavar='MOUNTPOINT', type=str, 
        help='The directory to mount on')
    parser.add_argument('--kubeconfig', dest='kubeconfig', 
        help='Path to the kubeconfig file')
    parser.add_argument('--cluster', dest='cluster', 
        help='The name of the kubeconfig cluster to use')
    parser.add_argument('--context', dest='context', 
        help='The name of the kubeconfig context to use')
    parser.add_argument('--user', dest='user', 
        help='The name of the kubeconfig user to use')
    return parser.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    fuse = FUSE(KubeFuse(args.mountpoint, args.kubeconfig, args.cluster, args.context),
                    args.mountpoint, foreground=True)

if __name__ == '__main__':
    main()
