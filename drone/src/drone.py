#!/usr/bin/env python
from dronekit import connect ,VehicleMode,LocationGlobalRelative
from flask import Flask, request, jsonify
import requests, threading

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property # To resolve a bug from flask-restplus
from flask_restplus import Api,Resource, fields, Namespace

from uav import Drone
import time,socket,threading,json

service_key  = 'reg_key'

# global varaibale that will be use for handling the drone object

drone=None
# list of mode that are enabled


# event variable to communicate between threads


class Connection(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global drone
        drone = Drone()
        check = False
        while not check:
            time.sleep(1)
            l = drone.vehicle.last_heartbeat
            if l != None:
                check = True
        print("Now we are connected to the drone ")
        time.sleep(2)
        t1=threading.Timer(5.0,drone.init_gps_lock)
        t1.start()
        # send pozyx data
        x,y,z = 0,0,0
        q = [1,0,0,0]
        while True:
            drone.pozyx_to_fc(x,y,z,q)
            time.sleep(0.2)



app = Flask(__name__)
drone_connection = Connection()
api = Api(app, version='1.0', title='@elab_servive  API',
    description='API Documentation',doc='/droneapi/v1/documentation')
#this instruction helps to get rid of the default namesapce in the UI swagger
api.namespaces.clear()
drone_api = Namespace('drones')
api.add_namespace(drone_api,path='/droneapi/v1/operations')

app.secret_key="dronekit"
# Threads that will be used to handle some request
t1=None
#
# @app.before_first_request
# def func():
#     global drone
#     try :
#         #drone=Drone( connect('tcp:192.168.0.14:5763', wait_ready=True ) )
#         drone=Drone( connect('udp:172.28.0.4:14553',wait_ready=True) )
#         print("before_first_request is running connection successfull")
#         time.sleep(5)
#         # #perform trilateration and get the pose and orientation
#         # x,y,z = 0,0,0
#         # q = [1,0,0,0]
#         # # send pozyx use a thread becuse of the infint loop
#         # th = threading.Thread(target=drone.pozyx_to_fc,args=(x,y,z,q))
#         # th.start()
#
#     except:
#         print ("Some other error!")
#     """def run_job():
#         print("before_first_request is running connection successfull" )
#         #time.sleep(0.0001)
#
#     thread=threading.Thread(target=run_job)
#     thread.start()"""

@app.route('/index')
def index():
    return "welcome to dronekit sitl service"

@app.route('/test')
def test():
    return "welcome to dronekit sitl 4444  service"


@app.route('/get_mode')
def get_state():
    global drone
    status=drone.get_vehicle_mode()
    return str(status)

@app.route('/get_pose')
def get_pose():
    global drone
    pose=drone.get_position()
    return str(pose['north'])

@app.route('/status')
def get_status():
    global drone
    status=drone.vehicle.armed
    return str(status)

@app.route('/arm',methods=['post'])
def arm():
    #respone=None
    global drone
    #get the value of the post request
    data = request.get_json()
    if ( data['command'] == "arm" ):
        print("basic pre-arm checks ")
        #dont arm until the autopilot is ready
        while not drone.vehicle.is_armable:
            print("waiting for vehicle to initialize")
            time.sleep(1)
        print("arming motors")
        #copter should arm in GUIDED mode
        drone.vehicle.mode=VehicleMode("GUIDED")
        time.sleep(1)
        drone.vehicle.armed=True
        response = {"result":"drone is armed"}
        time.sleep(1)
    return jsonify(response)

@app.route('/mode',methods=['post'])
def set_vehicle_mode():
    global drone
    posted_data=request.get_json()
    mode=str(posted_data["mode"])
    drone.set_vehicle_mode(mode)
    return "the mode habe been changed "

@app.route('/go_to_alt',methods=['post'])
def goto():
    global drone
    respone = None
    #alt = float( request.args.get('alt') )
    alt = request.args.get('alt')
    #credential=data["credential"]
    #get the credential of the mission user from the database
    #db_credential="first_test"
    #if db_credential== str(credential):
        #that means the user can fly in this area
        #drone.go_to_alt(alt)
    t1=threading.Thread(target=drone.go_to_alt, name="fc_thread", args=(alt,))
    t1.start()
    response = {"result":alt}
    time.sleep(0.0001)
    return jsonify(response)




class Arming(Resource):
    global drone
    rf = api.model('arming',{
        'service_key':fields.String,
        'command':fields.String
    })

    @api.doc(responses={
        200: 'Success',
        401: 'vehicle mot in arm mode',
        500: 'Bad request'
    })

    @api.expect(rf,validate=True)
    def post(self):
        """
            Allow to arm the drone
        """
        armed = None
        try:
            # get the request from the Controller service
            data = request.get_json()
            # we check if the request is coming from the controller service
            s_key = data['service_key']
            command = data['command']
            if (service_key == s_key and command == "arm"):
                armed = drone.arm_vehicle()
                if armed:
                    status_code = 200
                    msg ="vehicle armed "
                else :
                    status_code = 401
                    msg ="vehicle not in arm mode "
            resp = {
                "status_code":status_code,
                "msg": msg
            }
            return jsonify(resp)

        except:
            status_code = 500
            resp = {
                "status_code":status_code,
                "msg": "Internal server error"
            }
            return jsonify(resp)

class Takeoff(Resource):
    global drone
    rf = api.model('takeoff',{
        'service_key':fields.String,
        'command':fields.String,
        'altitude':fields.Integer
    })


    @api.doc(responses={
        200: 'Success',
        500: 'Bad request'
    })

    @api.expect(rf,validate=True)
    def post(self):
        """
            Allow to fly the drone to a desired altitude and then land
        """
        try:
            takeoff_data = request.get_json()
            s_key = takeoff_data['service_key']
            command = takeoff_data['command']
            if (service_key == s_key and command == "takeoff"):
                alt = takeoff_data['altitude']
                # call the takeoff function
                drone.pull_out(alt)
                status_code = 200
                resp = {
                    "status_code":status_code
                }
                return jsonify(resp)
        except:
            status_code = 500
            resp = {
                "status_code":status_code
            }
        return jsonify(resp)

class Goto(Resource):
    global drone
    rf = api.model('goto',{
        'service_key':fields.String,
        'command':fields.String,
        'x':fields.Integer(description="x(m) in NED "),
        'y':fields.Integer(description="y(m) in NED "),
        'z':fields.Integer(description="z(m) in NED ")
    })

    @api.doc(responses={
        200: 'Success',
        500: 'Bad request'
    })

    @api.expect(rf,validate=True)
    def post(self):
        """
            go to  a desired position
        """
        try:
            status_code = 200
            tatus_code = 208
            resp = {
                "status_code":status_code
            }
            return jsonify(resp)
        except:
            status_code = 500
            resp = {
                "status_code":status_code
            }
            return jsonify(resp)



class Data(Resource):
    global drone
    @api.errorhandler
    def get(self):
        """
            Allow to expose local psosition and battery status
        """
        #pose = drone.get_pose()
        pose = drone.get_pose()
        bsi = drone.get_bsi()
        data = {
            "x":pose['north'],
            "y":pose['east'],
            "z":pose['down'],
            "bsi":bsi
        }
        return jsonify(data)





drone_api.add_resource(Arming,'/arming')
drone_api.add_resource(Takeoff,'/takeoff')
drone_api.add_resource(Data,'/state')
drone_api.add_resource(Goto,'/goto')

# def start_runner():
#     def start_loop():
#         not_started = True
#         while not_started:
#             print("in start")
#             try:
#                 r = requests.get("http://dronekit:5000/index")
#                 if r.status_code == 200:
#                     not_started = False
#             except:
#                 print("service drone has not stated yet")
#         print("started runner")
#     th_start = threading.Thread(target=start_loop)
#     th_start.start()
#     # we ait until this thread terminates to call other thread
#     th_start.join()





if __name__ == '__main__':
    drone_connection.start()
    app.run(host='0.0.0.0',debug=True, threaded=True,use_reloader=False)
