import mongoengine as me
from flask_login import UserMixin

'''
"rx_metadata": [
        {
          "gateway_ids": {
            "gateway_id": "test"
          },
          "rssi": 42,
          "channel_rssi": 42,
          "snr": 4.2
        }
    ]
'''

class Logger(UserMixin, me.Document):
    meta = {'collection': 'logger'}
    nodetype = me.StringField()
    nodeID = me.StringField()
    datetime = me.StringField()
    numSat = me.StringField()
    sigLevel = me.StringField()
    Latitude = me.FloatField()
    Longitude = me.FloatField()
    Altitude = me.FloatField()
    msgType = me.StringField()
    message = me.StringField()
    rssi = me.IntField()
    channelRssi = me.IntField()
    snr = me.IntField()