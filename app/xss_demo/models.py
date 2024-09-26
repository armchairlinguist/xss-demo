from threading import RLock
from copy import deepcopy
from datetime import (
    datetime,
    timezone,
    )
import bcrypt


class _DB():
    _db = {
        'posts': [],
        'comments': [],
        'users': [],
        }
    _db_lock = RLock()

    def save(self, obj):
        lock = _DB._db_lock
        db = _DB._db
        klass = type(obj)
        with lock:
            data = deepcopy(obj.serialize())
            if obj.id is not None:
                # Make sure entry exists
                self.get(klass, obj.id)
                db[klass.__table__][obj.id] = data
            else:
                db[klass.__table__].append(data)
                obj.id = len(db[klass.__table__]) - 1
        return obj

    def get(self, klass, obj_id):
        lock = _DB._db_lock
        db = _DB._db
        with lock:
            try:
                data = db[klass.__table__][obj_id]
            except IndexError:
                data = None
            if not data:
                raise ValueError('Invalid ID')
            obj = klass.deserialize(deepcopy(data))
            obj.id = obj_id
        return obj

    def get_all(self, klass):
        lock = _DB._db_lock
        db = _DB._db
        result = []
        with lock:
            for obj_id, data in enumerate(db[klass.__table__]):
                if not data:
                    # Skip deleted items
                    continue
                obj = klass.deserialize(deepcopy(data))
                obj.id = obj_id
                result.append(obj)
        return result

    def delete(self, obj):
        lock = _DB._db_lock
        db = _DB._db
        klass = type(obj)
        with lock:
            # Make sure entry exists
            self.get(klass, obj.id)
            db[klass.__table__][obj.id] = None
            obj.id = None


DB = _DB()


def now():
    return datetime.now(timezone.utc)


class Post():
    __table__ = 'posts'

    def __init__(self, title, content, author, comment_ids=None, date=None):
        self.id = None
        self.title = title
        self.content = content
        self.author = author
        self.comment_ids = comment_ids if comment_ids else []
        self.date = date if date else now()

    def serialize(self):
        return {
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'comment_ids': self.comment_ids,
            'date': self.date,
            }

    @classmethod
    def deserialize(cls, data):
        title = data['title']
        content = data['content']
        author = data['author']
        comment_ids = data['comment_ids']
        date = data['date']
        return cls(title, content, author, comment_ids=comment_ids, date=date)

# TODO: Do something cool
class Comment():
    __table__ = 'comments'

    def __init__(self, message, author, post_id, date=None):
        self.id = None
        self.message = message
        self.author = author
        self.post_id = post_id
        self.date = date if date else now()

    def serialize(self):
        return {
            'message': self.message,
            'author': self.author,
            'post_id': self.post_id,
            'date': self.date,
            }

    @classmethod
    def deserialize(cls, data):
        message = data['message']
        author = data['author']
        post_id = data['post_id']
        date = data['date']
        return cls(message, author, post_id, date=date)


class User():
    __table__ = 'users'

    def __init__(self, username, password, hash_it=True):
        self.id = None
        self.username = username
        if hash_it:
            enc_pwd = password.encode('utf-8')
            self.password = bcrypt.hashpw(enc_pwd, bcrypt.gensalt())
        else:
            self.password = password

    def serialize(self):
        return {
            'username': self.username,
            'password': self.password,
            }

    @classmethod
    def deserialize(cls, data):
        username = data['username']
        password = data['password']
        return cls(username, password, hash_it=False)

    def password_correct(self, password):
        enc_pwd = password.encode('utf-8')
        return bcrypt.hashpw(enc_pwd, self.password) == self.password

