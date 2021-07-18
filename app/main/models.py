from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.ext.mutable import Mutable
import pickle as pickle

from app import db


class MutableTypeWrapper(Mutable):
    top_attributes = ['_underlying_object',
                      '_underlying_type',
                      '_last_state', 
                      '_snapshot_update', 
                      '_snapshot_changed', 
                      '_notify_if_changed',
                      'changed',
                      '__getstate__',
                      '__setstate__',
                      'coerce']

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableTypeWrapper):
            try:
                return MutableTypeWrapper(value)
            except:
                return Mutable.coerce(key, value)
        else:
            return value

    def __getstate__(self):
        return self._underlying_object

    def __setstate__(self, state):
        self._underlying_type = type(state)
        self._underlying_object = state

    def __init__(self, underlying_object, underlying_type=None):
        if (underlying_object is None and underlying_type is None):  
            print('Both underlying object and type are none.')
            raise RuntimeError('Unable to create MutableTypeWrapper with no underlying object or type.')

        if (underlying_object is not None):
            self._underlying_object = underlying_object
        else:
            self._underlying_object = underlying_type()

        if (underlying_type is not None):
            self._underlying_type = underlying_type
        else:
            self._underlying_type = type(underlying_object)

    def __getattr__(self, attr):
        if (attr in MutableTypeWrapper.top_attributes):
            return object.__getattribute__(self, attr)

        orig_attr = self._underlying_object.__getattribute__(attr)
        if callable(orig_attr):
            def hooked(*args, **kwargs):
                self._snapshot_update()
                result = orig_attr(*args, **kwargs)
                self._notify_if_changed()
                # prevent underlying from becoming unwrapped
                if result == self._underlying_object:
                    return self
                return result
            return hooked
        else:
            return orig_attr

    def __setattr__(self, attr, value):
        if (attr in MutableTypeWrapper.top_attributes):
            object.__setattr__(self, attr, value)
            return

        self._underlying_object.__setattr__(attr, value)

        self.changed()

    def _snapshot_update(self):
        self._last_state = pickle.dumps(self._underlying_object,
                                        pickle.HIGHEST_PROTOCOL)

    def _snapshot_changed(self):
        return self._last_state != pickle.dumps(self._underlying_object,
                                                pickle.HIGHEST_PROTOCOL)

    def _notify_if_changed(self):
        if (self._snapshot_changed()):
            self.changed()


class User(UserMixin, db.Model):
    """"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement='auto')
    username = db.Column(db.String)
    password = db.Column(db.String)
    characters = db.relationship('Character', backref='user', lazy=True, cascade='all, delete-orphan')
    current_character_first_name = db.Column(db.String, nullable=True)
    current_character_last_name = db.Column(db.String, nullable=True)
    
    def __init__(self, username):
        self.username = username
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Character(db.Model):

    __tablename__ = "characters"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    char = db.Column(MutableTypeWrapper.as_mutable(db.PickleType))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_number'), nullable=True)


class EnemySpawn(db.Model):
    __tablename__ = "enemies"
    __table_args__ = {'extend_existing':  True}

    id = db.Column(db.Integer, primary_key=True)
    enemy = db.Column(MutableTypeWrapper.as_mutable(db.PickleType))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_number'), nullable=True)
    stop = db.Column(db.Boolean)
    health = db.Column(db.Integer, nullable=True)


class Room(db.Model):

    __tablename__ = "rooms"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(MutableTypeWrapper.as_mutable(db.PickleType))
    room_number = db.Column(db.Integer)
    x=db.Column(db.Integer)
    y=db.Column(db.Integer)
    characters = db.relationship('Character', backref='room', lazy=True)
    enemies = db.relationship('EnemySpawn', backref='room', lazy=True)
    area_name = db.Column(db.String, db.ForeignKey('areas.area_name'), nullable=False)


class WorldArea(db.Model):

    __tablename__ = "areas"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, autoincrement='auto', primary_key=True)
    area = db.Column(MutableTypeWrapper.as_mutable(db.PickleType))
    area_name = db.Column(db.String)
    rooms = db.relationship('Room', backref='area', lazy=True)

db.create_all()