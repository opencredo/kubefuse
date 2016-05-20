from stat import S_IFDIR, S_IFLNK, S_IFREG, S_IFIFO
from time import time
import logging
import errno
from fuse import FuseOSError

class KubeFileSystem(object):
    def __init__(self, client):
        self.client = client

    def _stat_dir(self):
        return dict(st_mode=(S_IFDIR | 0555), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def _stat_file(self, client, path):
        data = path.do_action(client)
        now = time()
        return dict(st_mode=(S_IFREG | 0444), st_nlink=1,
                st_size=len(data), st_ctime=now, st_mtime=now,
                st_atime=now)

    def list_files(self, path):
        if not path.exists(self.client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
        if not path.is_dir():
            logging.info("not a directory")
            raise FuseOSError(errno.ENOTDIR)
        if path.object_id is not None: 
            if path.resource_type != 'pod':
                return path.SUPPORTED_ACTIONS
            else:
                return path.SUPPORTED_POD_ACTIONS
        if path.resource_type is not None:
            return self.client.get_entities(path.namespace, path.resource_type)
        if path.namespace is not None:
            return path.SUPPORTED_RESOURCE_TYPES
        return self.client.get_namespaces() # + ['all']

    def getattr(self, path):
        if not path.exists(self.client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
        if path.action is not None:
            return self._stat_file(self.client, path)
        return self._stat_dir()

    def read(self, path, size, offset):
        if not path.is_file():
            raise FuseOSError(errno.ENOENT)
        data = path.do_action(self.client)
        return data[offset:size + 1]
