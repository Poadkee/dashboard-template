import mongoengine as me
from flask_login import UserMixin

class DrawnItems(UserMixin, me.Document):
    meta = {'collection': 'drawnItems'}
    id_layer = me.StringField()
    item = me.StringField()