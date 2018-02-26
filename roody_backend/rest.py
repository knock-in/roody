from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from flask_cors import CORS
import psycopg2
import dateutil.parser
import datetime
import os
import threading


conn = psycopg2.connect(host="postgres", dbname="postgres", user="postgres", password=os.environ["POSTGRES_PASS"])
cur = conn.cursor()

class Roody(Resource):
    def get(self):
        try:
            parsed_datetime = dateutil.parser.parse(request.args.get('since'))
        except ValueError:
            abort(400, message="Bad Request")
        cur.execute("SELECT temperature, humidity, smoke, carbonous, time_stamp FROM roody WHERE time_stamp > %s ORDER BY time_stamp ASC;", (parsed_datetime, ))
        return [
                {
                    "temperature": entry[0],
                    "humidity": entry[1],
                    "smoke": entry[2],
                    "carbonous": entry[3],
                    "time_stamp": entry[4].isoformat() 
                } for entry in cur.fetchall()
               ] 

class Temperature(Resource):
    def get(self):
        try:
            parsed_datetime = dateutil.parser.parse(request.args.get('since'))
        except ValueError:
            abort(400, message="Bad Request")
        cur.execute("SELECT temperature, time_stamp FROM roody WHERE time_stamp > %s ORDER BY time_stamp ASC;", (parsed_datetime, ))
        return [ { "temperature": entry[0], "timestamp": entry[1].isoformat() } for entry in cur.fetchall() ]

class Humidity(Resource):
    def get(self):
        try:
            parsed_datetime = dateutil.parser.parse(request.args.get('since'))
        except ValueError:
            abort(400, message="Bad Request")
        cur.execute("SELECT humidity, time_stamp FROM roody WHERE time_stamp > %s ORDER BY time_stamp ASC;", (parsed_datetime, ))
        return [ { "humidity": entry[0], "timestamp": entry[1].isoformat() } for entry in cur.fetchall() ]

class Smoke(Resource):
    def get(self):
        try:
            parsed_datetime = dateutil.parser.parse(request.args.get('since'))
        except ValueError:
            abort(400, message="Bad Request")
        
        cur.execute("SELECT smoke, time_stamp FROM roody WHERE time_stamp > %s ORDER BY time_stamp ASC;", (parsed_datetime, ))
        return [ { "smoke": entry[0], "timestamp": entry[1].isoformat() } for entry in cur.fetchall() ]

class Carbonous(Resource):
    def get(self):
        try:
            parsed_datetime = dateutil.parser.parse(request.args.get('since'))
        except ValueError:
            abort(400, message="Bad Request")

        cur.execute("SELECT carbonous, time_stamp FROM roody WHERE time_stamp > %s ORDER BY time_stamp ASC;", (parsed_datetime, ))
        return [ { "carbonous": entry[0], "timestamp": entry[1].isoformat() } for entry in cur.fetchall() ]



class rest_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.app = Flask(__name__)
        CORS(self.app)
        self.api = Api(self.app)
        self.api.add_resource(Roody, '/')
        self.api.add_resource(Temperature, '/temperature')
        self.api.add_resource(Limits, '/limits')
        self.api.add_resource(Humidity, '/humidity')
        self.api.add_resource(Smoke, '/smoke')
        self.api.add_resource(Carbonous, '/carbonous')

    def run(self):
        self.app.run(threaded=True, host = '0.0.0.0')

cur.execute("SELECT temperature, humidity, carbonous, smoke FROM limits");
limits = cur.fetchone();
limits = {
        "temperature": limits[0],
        "humidity": limits[1],
        "carbonous": limits[2],
        "smoke": limits[3]
}


class Limits(Resource):
    def get(self):
        return limits
    def put(self):
        global limits
        for limit in request.json.keys():
            limits[limit] = float(request.json[limit])
        
        cur.execute("UPDATE limits SET temperature=%s, humidity=%s, carbonous=%s, smoke=%s", 
                (limits['temperature'], limits['humidity'], limits['carbonous'], limits['smoke'], ))
        conn.commit()
        return limits

