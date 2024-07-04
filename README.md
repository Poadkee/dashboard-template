# Dashboard Template (leaflet and flask)
before start this app you should install [mongodb](https://www.mongodb.com/try/download/community) and python3 on your localhost 

### Start
```
pip install -r requirements.txt
```

then, start this app with command</br>
```
python app.py
```
this you can access the site at http://localhost:5000/

### Using Docker(Optional)
#### create image
```
docker build -t <image_name>:latest .
```
#### create and run container
```
docker run -d -p <port>:<port> <image_name>
```

## Create Database

Create Database with following collections
- users
- drawnItems
- Loggers


DO NOT FORGET TO CREATE USER FOR LOGIN

PS. You can change these later (take a look at models folder)
