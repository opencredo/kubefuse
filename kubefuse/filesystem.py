from stat import S_IFDIR, S_IFLNK, S_IFREG, S_IFIFO
from time import time
import logging
import errno
from fuse import FuseOSError
from path import KubePath

class KubeFileSystem(object):
    def __init__(self, client):
        self.client = client
        self.open_files = {}

    def _stat_dir(self):
        return dict(st_mode=(S_IFDIR | 0555), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def _stat_file(self, client, path, mode=0444, size=None):
        data = path.do_action(client)
        if size is None:
            size = len(data)
        ts = path.get_creation_date_for_action_file(client)
        if ts is None:
            ts = time()
        return dict(st_mode=(S_IFREG | mode), st_nlink=1,
                st_size=size, st_ctime=ts, st_mtime=ts,
                st_atime=ts)

    def open(self, path):
        self.open_files[path] = KubePath().parse_path(path).do_action(self.client)

    def truncate(self, path, length):
        self.open_files[path] = self.open_files[path][:length]

    def write(self, path, buf, offset):
        self.open_files[path] = self.open_files[path][:offset] + buf
        return len(buf)

    def close(self, path):
        if path not in self.open_files:
            return
        logging.info("Path %s is now %s" % (path, self.open_files[path]))
        self.persist(path, self.open_files[path])
        del(self.open_files[path])
        # TODO delete from cache

    def sync(self, path):
        if path not in self.open_files:
            return
        self.persist(path, self.open_files[path])

    def persist(self, path, data):
        pass

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

    def getattr(self, p):
        path = KubePath().parse_path(p)
        mode = 0444 if path.action not in ['json', 'yaml'] else 0666
        if p in self.open_files:
            return self._stat_file(self.client, path, mode, len(self.open_files[p]))

        if not path.exists(self.client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
        if path.action is not None:
            mode = 0444 if path.action not in ['json', 'yaml'] else 0666
            return self._stat_file(self.client, path, mode)
        return self._stat_dir()

    def read(self, path, size, offset):
        if not path.is_file():
            raise FuseOSError(errno.ENOENT)
        data = path.do_action(self.client)
        return data[offset:size + 1]

