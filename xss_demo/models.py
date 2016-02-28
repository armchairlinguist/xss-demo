from threading import RLock
from copy import deepcopy
from datetime import (
    datetime,
    timezone,
    )


class _DB():
    _db = {
        'posts': [],
        'comments': [],
        }
    _db_lock = RLock()

    def save(self, obj):
        lock = _DB._db_lock
        db = _DB._db
        klass = type(obj)
        with lock:
            data = deepcopy(obj.serialize())
            if obj.id:
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

    def __init__(self, content, date=None):
        self.id = None
        self.content = content
        self.date = date if date else now()

    def serialize(self):
        return {
            'content': self.content,
            'date': self.date,
            }

    @classmethod
    def deserialize(cls, data):
        content = data['content']
        date = data['date']
        return cls(content, date=date)


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
