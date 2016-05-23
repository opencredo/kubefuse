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
        self.flushed = {}

    def _stat_dir(self):
        return dict(st_mode=(S_IFDIR | 0555), st_nlink=2,
                st_size=0, st_ctime=time(), st_mtime=time(),
                st_atime=time())

    def _stat_file(self, client, path, size=None):
        if size is None:
            size = len(path.do_action(client))
        ts = path.get_creation_date_for_action_file(client)
        if ts is None:
            ts = time()
        return dict(st_mode=(S_IFREG | path.get_mode()), st_nlink=1,
                st_size=size, st_ctime=ts, st_mtime=ts,
                st_atime=ts)

    def open_for_writing(self, path):
        if path not in self.open_files:
            self.open_files[path] = KubePath().parse_path(path).do_action(self.client)

    def open(self, path, fh):
        pass

    def truncate(self, path, length):
        self.open_for_writing(path)
        self.open_files[path] = self.open_files[path][:length]

    def write(self, path, buf, offset):
        self.open_for_writing(path)
        self.open_files[path] = self.open_files[path][:offset] + buf
        return len(buf)

    def close(self, path):
        if path not in self.open_files:
            return
        self.persist(path, self.open_files[path])
        del(self.open_files[path])
        del(self.flushed[path])
        p = KubePath().parse_path(path)
        self.client.delete_from_cache(p.namespace, p.resource_type, 
            p.object_id, p.action)

    def sync(self, path, dry_run=False):
        if path not in self.open_files:
            return
        self.persist(path, self.open_files[path], dry_run)

    def persist(self, path, data, dry_run=False):
        if path in self.flushed and data == self.flushed[path]:
            return 
        self.flushed[path] = data
        if not dry_run:
            self.client.replace(data)

    def list_files(self, path):
        p = KubePath().parse_path(path)
        if not p.exists(self.client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
        if not p.is_dir():
            logging.info("not a directory")
            raise FuseOSError(errno.ENOTDIR)
        if p.object_id is not None: 
            if p.resource_type != 'pod':
                return p.SUPPORTED_ACTIONS
            else:
                return p.SUPPORTED_POD_ACTIONS
        if p.resource_type is not None:
            return self.client.get_entities(p.namespace, p.resource_type)
        if p.namespace is not None:
            return p.SUPPORTED_RESOURCE_TYPES
        return self.client.get_namespaces() # + ['all']

    def getattr(self, path):
        p = KubePath().parse_path(path)
        if path in self.open_files:
            return self._stat_file(self.client, p, len(self.open_files[path]))
        if not p.exists(self.client):
            logging.info("path doesn't exist")
            raise FuseOSError(errno.ENOENT)
        if p.action is not None:
            return self._stat_file(self.client, p)
        return self._stat_dir()

    def read(self, path, size, offset):
        p = KubePath().parse_path(path)
        if not p.is_file():
            raise FuseOSError(errno.ENOENT)
        if path in self.flushed:
            data = self.flushed[path]
        else:
            data = p.do_action(self.client)
        return data[offset:offset + size]

