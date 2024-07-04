import mongoengine as me
from flask_login import UserMixin

class User(UserMixin, me.Document):
    meta = {'collection': 'users'}
    email = me.StringField(max_length=30)
    password = me.StringField()