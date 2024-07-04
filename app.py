from flask import Flask, render_template, jsonify, request, url_for, redirect
from flask_cors import CORS, cross_origin
from flask_socketio import send, emit, SocketIO
from flask_mongoengine import MongoEngine
from flask_bootstrap import Bootstrap5, SwitchField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import json
from models import User, Logger, DrawnItems
from forms import RegForm

app = Flask(__name__)
# Initialize cross origin
CORS(app)
# Initialize Bootstrap5 for jinja template engine
bootstrap = Bootstrap5(app)

# Inititalze database
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/Template'
}

# - It also creates databases and collections on the fly if they do not exist.
# - ref: https://docs.mongoengine.org/index.html
db = MongoEngine(app)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # set route for authentication

# Override user loader method for login_manager
@login_manager.user_loader
def load_user(user_id):
    # You can add some statement logic to handle user information.
    return User.objects(pk=user_id).first()

@app.route('/register', methods=['GET', 'POST']) 
# @login_required # comment this first in case you dont have any user
def register():
    # if current_user.is_authenticated == True:
    #     return redirect(url_for('index'))
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            existing_user = User.objects(email=form.email.data).first()
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                hey = User(email=form.email.data,password=hashpass).save()
                return redirect(url_for('users'))
                # login_user(hey)
                # return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('index'))
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = User.objects(email=form.email.data).first()
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/')
@login_required
def index():
    logs = Logger.objects().all()
    log_data = []
    log_id = []
    for log in logs:
        idType = (str(log.nodetype) + "_" + str(log.nodeID))
        if(idType not in log_id):
            log_id.append(idType)
        log_data.append({
            "id_node": log.nodeID,
            "type_node": log.nodetype,
            "timestamp": log.datetime,
            "latitude": log.Latitude,
            "longitude": log.Longitude,
            "altitude": log.Altitude,
            "msgType": log.msgType,
            "message": log.message,
            "sigLevel": log.sigLevel,
            "rssi": log.rssi,
            "channelRssi": log.channelRssi,
            "snr": log.snr,
        })
    log_id = sorted(log_id)
    
    items = DrawnItems.objects().all()
    item_data = []
    for item in items:
        item_data.append({
            "id_layer": item.id_layer,
            "item": item.item,
        })

    # location อ่างน้ำ
    start_lat = 7.007971021953185
    start_lon = 100.50422607027106
    if(len(log_data) > 0):
        start_lat = log_data[-1]['latitude']
        start_lon = log_data[-1]['longitude']

    # Login NOT Required
    # return render_template('index.html', start_map_position=[start_lat, start_lon], name="NoneLoginRequired", 
    #                        data=log_data, ids = log_id, item=item_data)

    # Login Required
    return render_template('index.html', start_map_position=[start_lat, start_lon], name=current_user.email, 
                           data=log_data, ids = log_id, item=item_data)

@app.route('/logging', methods = ['GET'])
@login_required
def logging():
    logs = Logger.objects().all()
    log_data = []
    for log in logs:
        log_data.append({
            "id_node": log.nodeID,
            "type_node": log.nodetype,
            "timestamp": log.datetime,
            "latitude": log.Latitude,
            "longitude": log.Longitude,
            "altitude": log.Altitude,
            "msgType": log.msgType,
            "message": log.message,
            "rssi": log.rssi,
            "channelRssi": log.channelRssi,
            "snr": log.snr,
        })
    return render_template('logging.html', data=log_data)

@app.route('/device', methods = ['GET'])
@login_required
def device():
    logs = Logger.objects().all()
    log_data = []
    for log in logs:
        idType = (str(log.nodetype) + "_" + str(log.nodeID))
        if(idType not in log_data):
            log_data.append(idType)
    log_data = sorted(log_data)
    return render_template('device.html', data=log_data)

@app.route('/users', methods = ['GET'])
@login_required
def users():
    logs = User.objects().all()
    log_data = []
    for log in logs:
        log_data.append(log)

    return render_template('users.html',name=str(current_user.email), data=log_data)

@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/history', methods = ['GET'])
@login_required
def history():
    start = request.args['start']
    end = request.args['end']
    logs = Logger.objects().all()
    log_data = []
    if(start!="live" or end!="live"):
        for log in logs:
            timeLog = datetime.strptime(log.datetime, "%Y-%m-%dT%H:%M:%S")
            timeLog_ms = (timeLog - datetime(1970, 1, 1)).total_seconds() * 1000
            if((int(start) < int(timeLog_ms)) and (int(timeLog_ms) < int(end))):
                log_data.append({
                    "id_node": log.nodeID,
                    "type_node": log.nodetype,
                    "timestamp": log.datetime,
                    "latitude": log.Latitude,
                    "longitude": log.Longitude,
                    "altitude": log.Altitude,
                    "msgType": log.msgType,
                    "message": log.message,
                    "sigLevel": log.sigLevel,
                    "rssi": log.rssi,
                    "channelRssi": log.channelRssi,
                    "snr": log.snr,
                })
    # else:
    #     for log in logs:
    #         log_data.append({
    #             "id_node": log.nodeID,
    #             "type_node": log.nodetype,
    #             "timestamp": log.datetime,
    #             "latitude": log.Latitude,
    #             "longitude": log.Longitude,
    #         })
    return jsonify(data=log_data)

@app.route('/hookme', methods = ['GET', 'POST'])
def hookme():
    print("START TO HOOKING")
    if request.method == 'POST':
        data = request.json
        sp_data = data['uplink_message']['decoded_payload']
        rx_data = data['uplink_message']['rx_metadata'][0]
        if rx_data:
            rx_data = {
                "rssi": 0,
                "channel_rssi": 0,
                "snr": 0
            }
        inserted_data = Logger(nodetype = sp_data['nodetype'],
                               nodeID = sp_data['nodeID'],
                               datetime = sp_data['datetime'],
                               numSat = sp_data['numSat'],
                               sigLevel = sp_data['sigLevel'],
                               Latitude = sp_data['Latitude'],
                               Longitude = sp_data['Longitude'],
                               Altitude = sp_data['Altitude'],
                               msgType = sp_data['msgType'],
                               message = sp_data['msgData'],
                               rssi = rx_data["rssi"],
                               channelRssi = rx_data["channel_rssi"],
                               snr = rx_data["snr"]).save()
        if inserted_data:
            # inserted_data = collection.insert_one(data)
            # print("Data received from Webhook is: ", data['uplink_message']['decoded_payload'], type(data))
            # print("Inserted document ID:", inserted_data['id'])
            
            # logs = Logger.objects().all()
            log_data = []
            # for log in logs:
            log_data.append({
                "id_node": inserted_data.nodeID,
                "type_node": inserted_data.nodetype,
                "timestamp": inserted_data.datetime,
                "latitude": inserted_data.Latitude,
                "longitude": inserted_data.Longitude,
                "altitude": inserted_data.Altitude,
                "msgType": inserted_data.msgType,
                "message": inserted_data.message,
                "rssi": inserted_data.rssi,
                "channelRssi": inserted_data.channelRssi,
                "snr": inserted_data.snr,
            })
            socketio.emit('get_live_data', log_data)

            # socket_temp = dict()
            # for i in inserted_data:
            #     if i != 'id':
            #         socket_temp[i] = inserted_data[i]
            # socketio.emit('get_live_data',json.dumps(socket_temp))
    return "Webhook received!"
        # print("Webhook received!")
        # inserted_data = collection.insert_one(data)
        # print("Inserted document ID:", inserted_data.inserted_id)

@app.route('/drawn', methods = ['GET', 'POST'])
@login_required
def drawn():
    items = request.args['items']
    id_layer = request.args['id_layer']
    item = DrawnItems(id_layer=id_layer,
                      item=items).save()
    
    item_data = {
        "id_layer": item.id_layer,
        "item": item.item,
    }
    # socketio.emit('get_drawn_data', item_data, include_self=True)
    return "drawn"

@app.route('/edited', methods = ['GET', 'POST'])
@login_required
def edited():
    id_layers = request.args['id_layers']
    props = request.args['properties']
    id_layers = id_layers.split("__")
    props = props.split("__")
    item_data = []
    for i in range(len(id_layers)):
        print("edited :", id_layers[i])
        item = DrawnItems.objects(id_layer = id_layers[i])
        item.update(item = props[i])
        item_data.append({
            "id_layer": id_layers[i],
            "item": props[i],
        })

    # socketio.emit('get_edited_data', item_data)
    return "edited"

@app.route('/deleted', methods = ['GET', 'POST'])
@login_required
def deleted():
    id_layers = request.args['id_layers']
    id_layers = id_layers.split("__")
    item_data = []
    for id_layer in id_layers:
        print("deleted :", id_layer)
        item = DrawnItems.objects(id_layer = id_layer).delete()
        item_data.append({"id_layer": id_layer})

    # socketio.emit('get_deleted_data', item_data)
    return "deleted"

if __name__ == '__main__':
    # app.run(host="192.168.4.2", port=5000, debug=True)
    app.run(port=5000, debug=True)
    # socketio.run(app, host="<server IP>", port=5000, debug=True)
    # socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)