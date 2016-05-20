from stat import S_IFDIR, S_IFLNK, S_IFREG, S_IFIFO
from time import time
import logging
import errno
from fuse import FuseOSError

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

    def _is_dir(self):
        return self.path.action is None
    def _is_file(self):
        return not(self._is_dir())

    def list_files(self, client):
        if not self.path.exists(client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
        if not self._is_dir():
            logging.info("not a file")
            raise FuseOSError(errno.ENOTDIR)
        if self.path.object_id is not None: 
            if self.path.resource_type != 'pod':
                return self.path.SUPPORTED_ACTIONS
            else:
                return self.path.SUPPORTED_POD_ACTIONS
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

