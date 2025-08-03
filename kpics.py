# -*- coding: utf-8 -*-
import cv2
import os
import glob
import pathlib
import hashlib
import numpy as np
import sys
import shutil
from urllib.parse import quote, urlencode
import datetime
import time
from humanfriendly import format_size, format_path, format_timespan
import sqlite3
# import json
# import re
# import time
# import pickle
# import time
# import matplotlib.pyplot as plt


_max_width = 1200
_max_height = 900

def show(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize(image):
    image_width, image_height = image.shape[:2]

    if image_width > _max_width or image_height > _max_height:
        proportion = image_width / image_height
        return cv2.resize(image, (_max_width, _max_height))

def md5(str):
    return hashlib.md5(str).hexdigest()

def samestat(s1, s2):
    """Test whether two stat results refer to the same file"""
    return (s1.st_dev, s1.st_ino) == (s2.st_dev, s2.st_ino)
import os
# Are two stat buffers (obtained from stat, fstat or lstat)
# describing the same file? 

# This is a more reliable way to compare files than comparing
# their names, as it works even if the files have been renamed,
# moved or are on different filesystems.

def get_file_stat(path):
    """Get the stat result for a file or directory."""
    try:
        return os.stat(path)
    except OSError as e:
        print(f"Error getting stat for {path}: {e}")
        return None

def get_file_size(path):
    """Get the size of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_size
    return None

def get_file_mtime(path):
    """Get the last modification time of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_mtime
    return None

def get_file_ctime(path):
    """Get the creation time of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_ctime
    return None

def get_file_atime(path):
    """Get the last access time of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_atime
    return None

def get_file_permissions(path):
    """Get the permissions of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_mode
    return None

def get_file_owner(path):
    """Get the owner of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_uid
    return None

def get_file_group(path):
    """Get the group of a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return stat.st_gid
    return None

def get_file_type(path):
    """Get the type of a file (regular file, directory, symlink, etc.)."""
    stat = get_file_stat(path)
    if stat is not None:
        if os.path.isfile(path):
            return 'file'
        elif os.path.isdir(path):
            return 'directory'
        elif os.path.islink(path):
            return 'symlink'
        else:
            return 'other'
    return None

def get_file_info(path):
    """Get comprehensive information about a file."""
    stat = get_file_stat(path)
    if stat is not None:
        return {
            'size': stat.st_size,
            'mtime': stat.st_mtime,
            'ctime': stat.st_ctime,
            'atime': stat.st_atime,
            'permissions': stat.st_mode,
            'owner': stat.st_uid,
            'group': stat.st_gid,
            'type': get_file_type(path),
        }
    return None

def get_file_info_str(path):
    """Get a string representation of file information."""
    info = get_file_info(path)
    if info is not None:
        return (
            f"File: {path}\n"
            f"Size: {info['size']} bytes\n"
            f"Last Modified: {datetime.datetime.fromtimestamp(info['mtime'])}\n"
            f"Created: {datetime.datetime.fromtimestamp(info['ctime'])}\n"
            f"Last Accessed: {datetime.datetime.fromtimestamp(info['atime'])}\n"
            f"Permissions: {oct(info['permissions'])}\n"
            f"Owner: {info['owner']}\n"
            f"Group: {info['group']}\n"
            f"Type: {info['type']}"
        )
    return "File not found or inaccessible."

def get_file_info_json(path):
    """Get file information in JSON format."""
    import json
    info = get_file_info(path)
    if info is not None:
        return json.dumps(info, indent=4, default=str)
    return json.dumps({"error": "File not found or inaccessible."}, indent=4)

def __get_builtin_constructor(name):
    """Return a constructor for the named hash algorithm, using the
    builtin Python implementation.
    """
    cache = {}
    try:
        if name in {'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'}:
            import _hashlib
            cache['md5'] = _hashlib.md5
            cache['sha1'] = _hashlib.sha1
            cache['sha224'] = _hashlib.sha224
            cache['sha256'] = _hashlib.sha256
            cache['sha384'] = _hashlib.sha384
            cache['sha512'] = _hashlib.sha512
        elif name in {'blake2b', 'blake2s'}:
            import _blake2
            cache['blake2b'] = _blake2.blake2b
            cache['blake2s'] = _blake2.blake2s
        elif name in {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
                      'shake_128', 'shake_256'}:
            import _sha3
            cache['sha3_224'] = _sha3.sha3_224
            cache['sha3_256'] = _sha3.sha3_256
            cache['sha3_384'] = _sha3.sha3_384
            cache['sha3_512'] = _sha3.sha3_512
            cache['shake_128'] = _sha3.shake_128
            cache['shake_256'] = _sha3.shake_256
        elif name in {'SHA1', 'sha1'}:
            import _sha1
            cache['SHA1'] = cache['sha1'] = _sha1.sha1
        elif name in {'MD5', 'md5'}:
            import _md5
            cache['MD5'] = cache['md5'] = _md5.md5
        elif name in {'SHA256', 'sha256', 'SHA224', 'sha224'}:
            import _sha2
            cache['SHA224'] = cache['sha224'] = _sha2.sha224
            cache['SHA256'] = cache['sha256'] = _sha2.sha256
        elif name in {'SHA512', 'sha512', 'SHA384', 'sha384'}:
            import _sha2
            cache['SHA384'] = cache['sha384'] = _sha2.sha384
            cache['SHA512'] = cache['sha512'] = _sha2.sha512
        elif name in {'blake2b', 'blake2s'}:
            import _blake2
            cache['blake2b'] = _blake2.blake2b
            cache['blake2s'] = _blake2.blake2s
        elif name in {'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'}:
            import _sha3
            cache['sha3_224'] = _sha3.sha3_224
            cache['sha3_256'] = _sha3.sha3_256
            cache['sha3_384'] = _sha3.sha3_384
            cache['sha3_512'] = _sha3.sha3_512
        elif name in {'shake_128', 'shake_256'}:
            import _sha3
            cache['shake_128'] = _sha3.shake_128
            cache['shake_256'] = _sha3.shake_256
    except ImportError:
        print(f"Error importing hash module for {name}: {sys.exc_info()[1]}")
        return None
    constructor = cache.get(name)
    if constructor is not None:
        return constructor
    raise ValueError(f'unsupported hash type {name}')

def get_hash_constructor(name):
    """Return a constructor for the named hash algorithm."""
    if name in {'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
                'blake2b', 'blake2s', 'sha3_224', 'sha3_256', 'sha3_384',
                'sha3_512', 'shake_128', 'shake_256'}:
        return __get_builtin_constructor(name)
    raise ValueError(f'unsupported hash type {name}')

def format_datetime(dt):
    """Format a datetime object as a string."""
    if isinstance(dt, datetime.datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dt, datetime.date):
        return dt.strftime('%Y-%m-%d')
    else:
        raise ValueError("Input must be a datetime or date object.")

def format_path(path):
    """Format a file path as a string."""
    if isinstance(path, str):
        return path
    elif isinstance(path, pathlib.Path):
        return str(path)
    else:
        raise ValueError("Input must be a string or pathlib.Path object.")
def format_size(size, binary=False):
    """Format a file size as a human-readable string."""
    if isinstance(size, int) or isinstance(size, float):
        if binary:
            return f"{size / (1024 ** 2):.2f} MiB"
        else:
            return f"{size / (1000 ** 2):.2f} MB"
    else:
        raise ValueError("Input must be an integer or float representing file size.")    
def format_timespan(seconds):
    """Format a timespan in seconds as a human-readable string."""
    if isinstance(seconds, (int, float)):
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"
    else:
        raise ValueError("Input must be an integer or float representing seconds.")

def scan_dir(_photos_dir_path):
    _photos = []
    _photo_list = {}
    print(_photos_dir_path)
    try:
    # if not os.path.isdir(_photos_dir_path):
        if type(_photos_dir_path) is not dict:
            _photos_dir_path = [_photos_dir_path]
        for _photos_dir in _photos_dir_path.values():
            print("Star scanning photos directory in: %s" % _photos_dir)
            for root, sub_folder, files in os.walk(_photos_dir):        
                if '_files' not in root:
                    print("root: %s" % root)
                    if len(files) > 0:
                        for _file in files:
                            _file_name = _file.endswith(_file)
                            _extension = pathlib.Path(_file).suffix
                            if(_extension in ('.jpg', '.jpeg', '.png')):
                                _full_path = os.path.join(root, _file)
                                print("Full path: %s" % _full_path)
                                _photos.append(_full_path)
                                _photo_list[len(_photo_list)] = _full_path

        return _photo_list
    except IOError:
        print('IO Error')
    except:
        print("Unexpected error:", sys.exc_info()[0])


def thumb(_photo_path):
    _thumb_dir = r'C:\Users\kogut\Documents\.kpics'

def gen_hash(data):
    """Generate an md5 hash from bytes or string."""
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()
    

class KpicsProcessor:
    def __init__(self, photos_dir_path, thumb_dir, thumb_height=153):
        self.init_dir = os.getcwd()
        
        # if type(photos_dir_path) is not dict:
        #     raise ValueError("photos_dir_path must be a dictionary with photo dir IDs as keys and paths as values.")
        self.photos_dir_path = photos_dir_path
        self.thumb_dir = thumb_dir
        self.thumb_height = thumb_height
    
        self.photos = scan_dir(self.photos_dir_path)
        self.thumb_dir_name = hashlib.md5(list(self.photos_dir_path.values())[0].encode()).hexdigest()
        
        self.thumb_dir_path = os.path.join(self.thumb_dir, self.thumb_dir_name)
        self.db_path = os.path.join(self.thumb_dir_path, '%s.db' % self.thumb_dir_name)
        
        self.links_dir_path = os.path.join(self.thumb_dir_path, 'links')
        self.html = ''
        self.db_init()
        path = photos_dir_path[0]
        directory = self.db_get_directory(path=path)

        if directory and 'id' in directory:
            directory_id = directory['id']
        else:

            directory_id = self.db_add_directory(path=path, name=os.path.basename(path),
                                        hash_path=gen_hash(path),ctime=get_file_ctime(path=path),mtime=get_file_mtime(path=path),
                                        size=get_file_size(path=path))
        self.directory_id = directory_id
        self.ensure_thumb_dir()
        self.ensure_links_dir()

    def db_connect(self):
        """Connect to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
        
    def db_close(self, conn):
        """Close the SQLite database connection."""
        if conn:
            try:
                conn.close()
            except sqlite3.Error as e:
                print(f"Error closing database connection: {e}")

    def db_execute(self, conn, query, params=None):
        """Execute a query on the SQLite database."""
        if conn:
            try:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor
            except sqlite3.Error as e:
                print(f"Database execution error: {e}")
                print(f"Query: {query}")
                return None
        return None
    
    def db_fetchone(self, cursor):
        """Fetch one result from the executed query."""
        if cursor:
            try:
                return cursor.fetchone()
            except sqlite3.Error as e:
                print(f"Error fetching data: {e}")
                return None
        return None
    
    def db_fetchmany(self, cursor, size=1):
        """Fetch many results from the executed query."""
        if cursor:
            try:
                return cursor.fetchmany(size)
            except sqlite3.Error as e:
                print(f"Error fetching data: {e}")
                return None
        return None
    
    def db_fetchone_as_dict(self, cursor):
        """Fetch one result from the executed query as a dictionary."""
        if cursor:
            try:
                row = cursor.fetchone()
                if row:
                    return dict(zip([column[0] for column in cursor.description], row))
                return None
            except sqlite3.Error as e:
                print(f"Error fetching data: {e}")
                return None
        return None
    
    def db_fetchall_as_dict(self, cursor):
        """Fetch all results from the executed query as a list of dictionaries."""
        if cursor:
            try:
                rows = cursor.fetchall()
                if rows:
                    return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
                return []
            except sqlite3.Error as e:
                print(f"Error fetching data: {e}")
                return []
        return []
    
    def db_add_directory(self, path, name, hash_path, ctime, mtime, size):
        """Insert a directory record into the database."""
        conn = self.db_connect()
        if conn:
            query = """
            INSERT INTO directorys (path, name, hash_path, ctime, mtime, size)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (path, name, hash_path, ctime, mtime, size)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                self.db_close(conn)
                return cursor.lastrowid
            else:
                self.db_close(conn)
                return None
        return None
    
    def db_get_directory(self, path):
        """Retrieve a directory record from the database by path."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM directorys WHERE path = ?"
            params = (path,)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                result = self.db_fetchone_as_dict(cursor)
                self.db_close(conn)
                return result
            else:
                self.db_close(conn)
                return None
        return None

    def db_get_directory_by_id(self, directory_id):
        """Retrieve a directory record from the database by ID."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM directorys WHERE id = ?"
            params = (directory_id,)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                result = self.db_fetchone_as_dict(cursor)
                self.db_close(conn)
                return result
            else:
                self.db_close(conn)
                return None
        return None
    
    def db_get_all_directories(self):
        """Retrieve all directory records from the database."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM directorys"
            cursor = self.db_execute(conn, query)
            if cursor:
                results = self.db_fetchall_as_dict(cursor)
                self.db_close(conn)
                return results
            else:
                self.db_close(conn)
                return []
        return []
    
    def db_update_directory(self, directory_id, path=None, name=None, hash_path=None, ctime=None, mtime=None, size=None):
        """Update a directory record in the database."""
        conn = self.db_connect()
        if conn:
            query = "UPDATE directorys SET "
            params = []
            if path is not None:
                query += "path = ?, "
                params.append(path)
            if name is not None:
                query += "name = ?, "
                params.append(name)
            if hash_path is not None:
                query += "hash_path = ?, "
                params.append(hash_path)
            if ctime is not None:
                query += "ctime = ?, "
                params.append(ctime)
            if mtime is not None:
                query += "mtime = ?, "
                params.append(mtime)
            if size is not None:
                query += "size = ? "
                params.append(size)
            else:
                query = query.rstrip(', ')
            query += "WHERE id = ?"
            params.append(directory_id)
            cursor = self.db_execute(conn, query, tuple(params))
            self.db_close(conn)
            return cursor
        return None
    
    def db_delete_directory(self, directory_id):
        """Delete a directory record from the database by ID."""
        conn = self.db_connect()
        if conn:
            query = "DELETE FROM directorys WHERE id = ?"
            params = (directory_id,)
            cursor = self.db_execute(conn, query, params)
            self.db_close(conn)
            return cursor
        return None
    
    def db_add_photo(self, path, directory_id, width, height, thumb_path, thumb_width, thumb_height, ctime, mtime, size, created):
        """Insert a photo record into the database."""
        conn = self.db_connect()
        if conn:
            query = """
            INSERT INTO photos (path, directory_id, width, height, thumb_path, thumb_width, thumb_height, ctime, mtime, size, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (path, directory_id, width, height, thumb_path, thumb_width, thumb_height, ctime, mtime, size, created)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                self.db_close(conn)
                return cursor.lastrowid
            else:
                self.db_close(conn)
                return None
        return None
    
    def db_get_photo(self, photo_id):
        """Retrieve a photo record from the database by ID."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM photos WHERE id = ?"
            params = (photo_id,)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                result = self.db_fetchone_as_dict(cursor)
                self.db_close(conn)
                return result
            else:
                self.db_close(conn)
                return None
        return None
    
    def db_get_photos_by_directory(self, directory_id):
        """Retrieve all photos from the database by directory ID."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM photos WHERE directory_id = ?"
            params = (directory_id,)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                results = self.db_fetchall_as_dict(cursor)
                self.db_close(conn)
                return results
            else:
                self.db_close(conn)
                return []
        return []
    
    def db_get_all_photos(self):
        """Retrieve all photos from the database."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM photos"
            cursor = self.db_execute(conn, query)
            if cursor:
                results = self.db_fetchall_as_dict(cursor)
                self.db_close(conn)
                return results
            else:
                self.db_close(conn)
                return []
        return []
    
    def db_update_photo(self, photo_id, path=None, directory_id=None, thumb_path=None, thumb_width=None, thumb_height=None, ctime=None, mtime=None, size=None):
        """Update a photo record in the database."""
        conn = self.db_connect()
        if conn:
            query = "UPDATE photos SET "
            params = []
            if path is not None:
                query += "path = ?, "
                params.append(path)
            if directory_id is not None:
                query += "directory_id = ?, "
                params.append(directory_id)
            if thumb_path is not None:
                query += "thumb_path = ?, "
                params.append(thumb_path)
            if thumb_width is not None:
                query += "thumb_width = ?, "
                params.append(thumb_width)
            if thumb_height is not None:
                query += "thumb_height = ?, "
                params.append(thumb_height)
            if ctime is not None:
                query += "ctime = ?, "
                params.append(ctime)
            if mtime is not None:
                query += "mtime = ?, "
                params.append(mtime)
            if size is not None:
                query += "size = ? "
                params.append(size)
            else:
                query = query.rstrip(', ')
            query += "WHERE id = ?"
            params.append(photo_id)
            cursor = self.db_execute(conn, query, tuple(params))
            self.db_close(conn)
            return cursor
        return None
    
    def db_delete_photo(self, photo_id):
        """Delete a photo record from the database by ID."""
        conn = self.db_connect()
        if conn:
            query = "DELETE FROM photos WHERE id = ?"
            params = (photo_id,)
            cursor = self.db_execute(conn, query, params)
            self.db_close(conn)
            return cursor
        return None
    
    def db_add_link(self, photo_id, link):
        """Insert a link record into the database."""
        conn = self.db_connect()
        if conn:
            query = """
            INSERT INTO links (photo_id, link)
            VALUES (?, ?)
            """
            params = (photo_id, link)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                self.db_close(conn)
                return cursor.lastrowid
            else:
                self.db_close(conn)
                return None
        return None
    
    def db_get_links_by_photo(self, photo_id):
        """Retrieve all links for a photo from the database by photo ID."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM links WHERE photo_id = ?"
            params = (photo_id,)
            cursor = self.db_execute(conn, query, params)
            if cursor:
                results = self.db_fetchall_as_dict(cursor)
                self.db_close(conn)
                return results
            else:
                self.db_close(conn)
                return []
        return []
    
    def db_delete_link(self, link_id):
        """Delete a link record from the database by ID."""
        conn = self.db_connect()
        if conn:
            query = "DELETE FROM links WHERE id = ?"
            params = (link_id,)
            cursor = self.db_execute(conn, query, params)
            self.db_close(conn)
            return cursor
        return None
    
    def ensure_thumb_dir(self):
        """Ensure the thumbnail directory exists."""
        if not os.path.isdir(self.thumb_dir_path):
            try:
                os.makedirs(self.thumb_dir_path)
                print(f"Thumbnail directory created at: {self.thumb_dir_path}")
            except OSError as e:
                print(f"Error creating thumbnail directory: {e}")
        else:
            print(f"Thumbnail directory already exists: {self.thumb_dir_path}")

    def ensure_links_dir(self):
        """Ensure the links directory exists."""
        if not os.path.isdir(self.links_dir_path):
            try:
                os.makedirs(self.links_dir_path)
                print(f"Links directory created at: {self.links_dir_path}")
            except OSError as e:
                print(f"Error creating links directory: {e}")
        else:
            print(f"Links directory already exists: {self.links_dir_path}")

    def __str__(self):
        """Return a string representation of the KpicsProcessor instance."""
        return f"KpicsProcessor(photos_dir_path={self.photos_dir_path}, thumb_dir={self.thumb_dir}, thumb_height={self.thumb_height})"
    
    def __repr__(self):
        """Return a detailed string representation of the KpicsProcessor instance."""
        return (f"KpicsProcessor(photos_dir_path={self.photos_dir_path}, "
                f"thumb_dir={self.thumb_dir}, thumb_height={self.thumb_height}, "
                f"thumb_dir_path={self.thumb_dir_path}, db_path={self.db_path})")
    
    def __del__(self):
        """Destructor for the KpicsProcessor instance."""
        print(f"Deleting KpicsProcessor instance: {self}")
        # Optionally, you can close the database connection here if needed.
        # self.db_close(self.conn)  # Assuming self.conn is the database connection.

    

    def db_init(self):
        """
        Initializes the database by establishing a connection, creating necessary tables,
        and handling any errors that occur during initialization.

        Prints the database path, success, or error messages as appropriate.

        Returns:
            None
        """
        print( "Initializing database at: %s" % self.db_path)
        """Initialize the database by creating necessary tables."""
        conn = self.db_connect()
        if conn:
            try:
                self.db_create_table()
                print("Database initialized successfully.")
            except sqlite3.Error as e:
                print(f"Error initializing database: {e}")
            finally:
                self.db_close(conn)
        else:
            print("Failed to connect to the database.")

    def db_execute_query(self, query, params=None):
        """Execute a query on the SQLite database."""
        conn = self.db_connect()
        if conn:
            try:
                cursor = self.db_execute(conn, query, params)
                if cursor:
                    self.db_close(conn)
                    return cursor
                else:
                    self.db_close(conn)
                    return None
            except sqlite3.Error as e:
                print("Error execute query")
                print(query)
            finally:
                self.db_close(conn)
        return None

    def db_fetchall(self, cursor):
        """Fetch all results from the executed query."""
        if cursor:
            try:
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching data: {e}")
                return None
        return None
    

    def db_create_table_directorys(self):
        """Create the directorys table in the SQLite database."""
        query = """
        CREATE TABLE IF NOT EXISTS directorys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            hash_path TEXT NOT NULL,
            ctime TEXT NOT NULL,
            mtime TEXT NOT NULL,
            size INTEGER NULL
        );
        """
        self.db_execute_query(query=query)

    def db_create_table_photos(self):
        # Create the photos table with necessary fields
        query = """
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            directory_id INTEGER NOT NULL,
            thumb_path TEXT NOT NULL,
            thumb_width INTEGER NOT NULL,
            thumb_height INTEGER NOT NULL,
            ctime TEXT NOT NULL,
            mtime TEXT NOT NULL,
            size INTEGER NOT NULL,
            created TEXT NOT NULLs
        );
        """
        self.db_execute_query(query=query)

    def db_create_table_links(self):
        """Create the links table in the SQLite database."""
        query = "CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY AUTOINCREMENT, photo_id INTEGER, link TEXT, FOREIGN KEY(photo_id) REFERENCES photos(id));"
        self.db_execute_query(query=query)

    def db_create_table_settings(self):
        query = "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);"
        query += "INSERT OR IGNORE INTO settings (key, value) VALUES ('thumb_height', ?);"
        params = (self.thumb_height)
        self.db_execute_query(query=query, params=params)

    def db_create_indexes(self):
        query = "CREATE INDEX IF NOT EXISTS idx_photos_path ON photos (path);"
        query += "CREATE INDEX IF NOT EXISTS idx_photos_thumb_path ON photos (thumb_path);"
        query += "CREATE INDEX IF NOT EXISTS idx_photos_ctime ON photos (ctime);"
        query += "CREATE INDEX IF NOT EXISTS idx_photos_mtime ON photos (mtime);"
        query += "CREATE INDEX IF NOT EXISTS idx_photos_size ON photos (size);"
        query += "CREATE INDEX IF NOT EXISTS idx_photos_thumb_width ON photos (thumb_width);"
        query += "CREATE INDEX IF NOT EXISTS idx_photos_thumb_height ON photos (thumb_height);"
        query += "CREATE UNIQUE INDEX IF NOT EXISTS idx_photos_unique ON photos (path, thumb_path);"
        query += "CREATE INDEX IF NOT EXISTS idx_links_photo_id ON links (photo_id);"
        query += "CREATE UNIQUE INDEX IF NOT EXISTS idx_links_unique ON links (photo_id, link);"
        self.db_execute_query(query=query)

    def db_create_table(self):
        self.db_create_table_directorys()
        self. db_create_table_photos()
        self.db_create_table_links()
        # self.db_create_table_settings()
        # self.db_create_indexes()    
        # query = """
        # PRAGMA journal_mode = WAL;
        # PRAGMA synchronous = NORMAL;
        # PRAGMA cache_size = 10000;
        # PRAGMA temp_store = MEMORY;
        # PRAGMA page_size = 4096;
        # PRAGMA locking_mode = NORMAL;
        # PRAGMA auto_vacuum = FULL;
        # PRAGMA secure_delete = ON;
        # PRAGMA foreign_keys = ON;
        # PRAGMA encoding = 'UTF-8';
        # PRAGMA case_sensitive_like = ON;
        # PRAGMA busy_timeout = 5000;
        # PRAGMA page_count = 10000;
        # PRAGMA user_version = 1;
        # PRAGMA optimize;
        # PRAGMA temp_store_directory = 'temp';
        # PRAGMA cache_spill = ON;
        # """
        # self.db_execute_query(query=query)


    def db_insert_photo(self, path, directory_id, width, height, thumb_path, thumb_width, thumb_height, ctime, mtime, size, created):
        """Insert a photo record into the database."""
        conn = self.db_connect()
        if conn:
            query = """
            INSERT INTO photos (path, directory_id, width, height, thumb_path, thumb_width, thumb_height, ctime, mtime, size, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (path,  self.directory_id, width, height, thumb_path, thumb_width, thumb_height, ctime, mtime, size, created)
            self.db_execute(conn, query, params)
            self.db_close(conn)
    
    def db_get_photos(self):
        """Retrieve all photos from the database."""
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM photos"
            cursor = self.db_execute(conn, query)
            photos = self.db_fetchall(cursor)
            self.db_close(conn)
            return photos
        return None

    def db_get_photo_by_path(self, path):
        conn = self.db_connect()
        if conn:
            query = "SELECT * FROM photos WHERE path = ?"
            params = (path,)
            cursor = self.db_execute(conn, query, params)
            photo = self.db_fetchone(cursor)
            self.db_close(conn)
            return photo
        return None

    def db_delete_photo(self, photo_id):
        """Delete a photo record from the database by ID."""
        conn = self.db_connect()
        if conn:
            query = "DELETE FROM photos WHERE id = ?"
            params = (photo_id,)
            self.db_execute(conn, query, params)
            self.db_close(conn)

    def add_html(self, html):
        self.html += html

    def get_external_links(self, path):
        links_path = os.path.join(os.path.dirname(path), 'info.txt')
        if os.path.exists(links_path):
            f = open(links_path, 'r')
            links = f.readlines()
            for l in links:
                self.add_html('<span class="photo_links"><a href="%s" title="%s">link</a></span>' % (l, l))

    def ensure_links_dir(self):
        if not os.path.isdir(self.links_dir_path):
            os.mkdir(self.links_dir_path)
            print("Create dir for links in: %s" % self.links_dir_path)
        else:
            print("Links dir already exists: %s" % self.links_dir_path)

    def ensure_thumb_dir(self):
        if not os.path.isdir(self.thumb_dir_path):
            os.mkdir(self.thumb_dir_path)
            print("Create dir for thumb files in: %s" % self.thumb_dir_path)

    def process_photos(self):
        id = 0
        for photo_id in self.photos:
            path = self.photos[photo_id]
            hash = gen_hash(path.encode())

            thumb_name = "%s.%s" % (hash, path.split('.')[-1])
            thumb_full_path = os.path.join(self.thumb_dir_path, thumb_name)
            if os.path.isfile(path):
                if not os.path.isfile(thumb_full_path):
                    os.chdir(os.path.dirname(path))
                    photo = cv2.imread(os.path.basename(path))
                    if photo is None:
                        print("Ignoring wrong photo file: %s" % path)
                        continue
                    print("photo shape for: %s" % path)
                    photo_height, photo_width = photo.shape[:2]
                    thumb_height = self.thumb_height
                    thumb_width = int((thumb_height * photo_width) / photo_height)
                    thumb = cv2.resize(photo, (int(thumb_width), int(thumb_height)), thumb_width/photo_width, thumb_height/photo_height)
                    cv2.imwrite(thumb_full_path, thumb)
                else:
                    os.chdir(os.path.dirname(path))
                    photo = cv2.imread(os.path.basename(path))
                    photo_height, photo_width = photo.shape[:2]
                    print("Thumb file already exists: %s" % thumb_full_path)
                    os.chdir(os.path.dirname(thumb_full_path))
                    thumb = cv2.imread(os.path.basename(thumb_full_path))
                    thumb_height, thumb_width = thumb.shape[:2]
                # link = os.path.join(self.links_dir_path, thumb_name)
                # if not os.path.islink(link):
                #     os.symlink(path, link)
                #     print("Create symlink for thumb: %s" % link)
                photo_db = self.db_get_photo_by_path(path=path)
                if photo_db is None:
                    self.db_add_photo(path=path, directory_id=self.directory_id, width=photo_width,
                                    height=photo_height,thumb_path=thumb_full_path,thumb_width=thumb_width,
                                    thumb_height=thumb_height,ctime=get_file_ctime(path=path),mtime=get_file_mtime(path=path),size=get_file_size(path=path),created=int(time.time()))
                self.add_html_photo(path, thumb_full_path, thumb_width, thumb_height, id)
                
                id += 1
                os.chdir(self.init_dir)

    def add_html_photo(self, path, thumb_full_path, thumb_width, thumb_height, id):
        self.add_html('<a id="photo-%s" href="%s" class="thumb" title="%s in %s">' % (str(id), path, os.path.basename(path), os.path.dirname(path)))
        self.add_html('<img src="%s" alt="%s" width="%s" height="%s"/>' % (thumb_full_path, os.path.basename(path), str(thumb_width), str(thumb_height)))
        self.add_html('<span class="photo_info">')
        self.add_html('<span class="photo_filename" title="Nazwa pliku">%s</span>' % os.path.basename(path))
        self.add_html('<span class="photo_ctime" title="Data utworzenia">%s</span>' % datetime.datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S'))
        self.add_html('<span class="photo_mtime" title="Data modyfikacji">%s</span>' % datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S'))
        self.add_html('<span class="photo_size" title="Rozmiar pliku">%s</span>' % format_size(os.path.getsize(path), binary=True))
        self.get_external_links(path)
        self.add_html('</span>')
        self.add_html('</a>')
        # self.add_html('<script>document.getElementById("photo-%s").scrollIntoView({ behavior: "smooth" });</script>' % str(id))


    def generate_html(self, html_name='index.html'):
        html_path = os.path.join(self.thumb_dir_path, html_name)
        # template_dir = os.path.dirname(html_path)
        template_dir = r'Y:\dev\kpics\template\kpics'
        if not os.path.isdir(template_dir):
            template_head_path = r'Y:\dev\topik-1\template\kpics\head_index.html'
            template_end_path = r'Y:\dev\topik-1\template\kpics\end_index.html'
            css = r'Y:\dev\topik-1\template\kpics\index.css'
        else:
            template_head_path = os.path.join(template_dir, 'head_index.html')
            template_end_path = os.path.join(template_dir, 'end_index.html')
            css = os.path.join(template_dir, 'index.css')
        if not os.path.isfile(template_head_path) or not os.path.isfile(template_end_path):
            raise FileNotFoundError("Template files not found in: %s" % template_dir)
        
        # template = ''
        with open(html_path, 'w', encoding="utf-8") as file_out:
            with open(template_head_path, "r", encoding="utf-8") as file_in:
                lines = file_in.readlines()
                for line in lines:
                    file_out.writelines(line)
                    # template += line
            file_in.close()
            file_out.writelines(self.html)
            # template += self.html

            template_footer = ''
            with open(template_end_path, "r", encoding="utf-8") as file_in:
                lines = file_in.readlines()
                for line in lines:
                    file_out.writelines(line)
                    # template_footer += line
            file_in.close()
        file_out.close()
        css_path = os.path.join(self.thumb_dir_path, os.path.basename(css))
        if not os.path.isfile(css_path) or os.path.getsize(css_path) != os.path.getsize(css):
            shutil.copy2(css, css_path)


if __name__ == '__main__':
    # photos_dir_dict = {0: r'K:\trainman\fb'}
    # photos_dir_dict[2] = r'Y:\Pictures\instagram'
    photos_dir_dict = {0: r'C:\Users\kogut\Pictures\sky'}
    
    processor = KpicsProcessor(
        photos_dir_path=photos_dir_dict,
        thumb_dir=r'C:\Users\kogut\Documents\.kpics',
        thumb_height=153
    )
    processor.process_photos()
    _html = processor.html
    _thumb_dir_path = processor.thumb_dir_path

    processor.generate_html()
    print("HTML generated in: %s" % _thumb_dir_path)
    print("HTML file: %s" % os.path.join(_thumb_dir_path, 'index.html'))
    print("Photos processed: %d" % len(processor.photos))
    print("HTML generated: %d" % len(processor.html))

