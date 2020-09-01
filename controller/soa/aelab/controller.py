from aelab import app, mail, api, redis

from flask import render_template, url_for,flash, redirect, request, jsonify, json, abort
from datetime import datetime, timedelta
from flask_mail import Message
from flask_restplus import Resource, fields, Namespace
from aelab.models import AccreditationModel
from datetime import datetime, timezone
from shapely.geometry import Point, Polygon
import uuid,requests,json,time
import pytz


#secret_key for communicating with the drone service
key = "reg_key"

max_alt = 3 # max altitude of the room

covered_area = Polygon([(0,0),(0,4),(4,4),(4,0)])

restricted_zone = Polygon([(2.5,3.5),(3.5,3.5),(3.5,2.5),(2.5,2.5)])

def check_init_drone_position():
    b = False
    r = requests.get("http://drone:5000/droneapi/v1/operations/state")
    try:
        pose = r.json()
        p = Point(pose["x"],pose["y"])
        if p.within(covered_area):
            b = True

    except (ValueError):
        print("there is no data ")
    return b

class room_location:
    def __init__(self):
        self.x1 = 0.3
        self.x2 = 4
        self.y1 = 0.3
        self.y2 = 4

    def set_covered_area(self,x_min,x_max,y_min,y_max):
        self.x1 = x_min
        self.x2 = x_max
        self.y1 = y_min
        self.y2 = y_max
        return {
            "x1":self.x1,
            "x2":self.x2,
            "y1":self.y1,
            "y2":self.y2
        }

Acc_api = Namespace('Accreditations')
Mission_api = Namespace('Missions')
#server_api = Namespace('Missions')
api.add_namespace(Acc_api,path='/middleapi')
api.add_namespace(Mission_api,path='/middleapi')
class PreCheckFlight(Resource):


    def checkformat(self,hour,duration,date):
        # Intialize the boolean value to true
        """ check the hour format """
        try:
            h = datetime.strptime(hour,'%H:%M:%S')
            d =  datetime.strptime(str(duration),'%M')
            dt = datetime.strptime(date,'%Y-%m-%d')
            status_code = 201
        except (ValueError,TypeError):
              status_code = 400
        return status_code

    rf1 = api.model('credential',{
             'username': fields.String,
             'drone_name': fields.String,
             'date': fields.String(description="date with format yyyy-mm-dd"),
             'duration':fields.String(description="%MM"),
             'hour':fields.String(description="%HH:%MM:%SS"),
             'altitude':fields.Integer,
             'radius':fields.Integer
    })
    @api.expect(rf1,validate=True)
    def post(self):
        resp = None
        credential_data = request.get_json()
        date = credential_data['date']
        hour = credential_data['hour']
        duration = credential_data['duration']
        status_code = self.checkformat(hour,duration,date)
        # check if the username exist and drone exist
        # check if time is not < to the time at the request

        if(status_code != 400 ):
            # we handle the request
            acc_model=AccreditationModel()
            try:
                rs = acc_model.flight_approval(credential_data)
                code = rs["status_code"]
                if code == 401:
                    resp = {
                        "status_code":rs['status_code'],
                        "msg":rs['message']
                    }
                    #return jsonify(resp)
                elif code == 402:
                    resp = {
                        "status_code":rs['status_code'],
                        "msg":rs['message']
                    }
                elif code == 405:
                    resp = {
                        "status_code":rs['status_code'],
                        "msg":rs['message']
                    }
                else:
                    resp = {
                        "status_code":rs['status_code'],
                        "msg":rs['message']
                    }
            except:
                status_code = 403
                msg = "try again, something is wrong"
                resp = {
                "status_code":status_code,
                "msg":msg
                }
        else:
            msg = "Error in valuetype "
            resp = {
            "status_code":status_code,
            "msg":msg
            }
        return jsonify(resp)

class Arming(Resource):

    rf = api.model('arming',{
             'clearance': fields.String(description="Check the clearance in your mail")
    })
    @api.doc(responses={
        200: 'Success',
        400: 'operation denied,the key does not exist',
        401: 'operation denied,the key is no longer valid',
        402: 'drone is not in the covered area',
        500: 'Internal server error '
    })

    @api.expect(rf,validate=True)
    def post(self):
        """ Arm a drone """
        mission_data = request.get_json()
        # check the initial position of the drone
        pos = check_init_drone_position()

        if pos:
            clearance = mission_data['clearance']
            acc = AccreditationModel()

            req = acc.check_clearance(clearance)
            # we check if the dictionary is not empty
            if  bool(req):
                """ the user can  send command only between a certain time  """
                s = req["start_time"]
                e = req["end_time"]
                # we convert the string into dattime object
                start = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                end = datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
                # we send the rquest if and only if we are in the range time
                #while True:
                # utcnow = datetime.now(tz=pytz.UTC)
                # dtnow = utcnow.astimezone(pytz.timezone('Europe/Berlin'))
                # dtstr = str(dtnow)
                # dt = dtstr.split('.')[0]
                # dtime = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                #current_time = datetime.today()
                current_time = acc.get_current_time()
                if (current_time > start and current_time < end):
                    # we can send instructions to the drone
                    mission_type = "arm"

                    input = {
                        "command":str(mission_type),
                        "service_key":key
                    }
                    # we send the request to the drone
                    url="http://drone:5000/droneapi/v1/operations/arming"
                    try:
                        resp = requests.post(url,json=input)
                        resp.raise_for_status()
                    except requests.exceptions.HTTPError as httpErr:
                        print("httpError, mission request can be posted:", httpErr)
                    #get back the answer from the server
                    try :
                        result=resp.json()
                        #time.sleep(0.0005)
                    except (ValueError):
                        result = {"result":"json test error"}
                    resp = result
                    return jsonify(resp)
                else :
                    resp = {"status_code":401,
                            "msg": "operation denied,the key is no longer valid"
                    }

                # return jsonify({"message":str(datetime.now())})
            else :
                resp = {"status_code":400,
                        "msg": "operation denied,this key does not exist"
                }

        else:

            resp = {"status_code":402,
                    "msg": "operation denied, the drone is not in a covered area"
            }

        return jsonify(resp)

class Takeoff(Resource):

    rf = api.model('takeoff',{
             'altitude': fields.Integer,
             'clearance': fields.String(description="Check the clearance in your mail")
    })

    @api.doc(responses={
        200: 'Success',
        400: 'operation denied,the key does not exist',
        401: 'operation denied,the key is no longer valid',
        402: 'operation denied,altitude too high,risk of coolision',
        500: 'Internal server error '
    })
    @api.expect(rf)
    def post(self,validate=True):
        """ fly the drone to a defined altitude  """
        takeoff_data = request.get_json()
        clearance = takeoff_data['clearance']
        alt = takeoff_data['altitude']
        acc = AccreditationModel()


        req = acc.check_clearance(clearance)
        # we check if the dictionary is not empty
        if  bool(req):
            """ the user can  send command only between a certain time  """
            s = req["start_time"]
            e = req["end_time"]
            # we convert the string into dattime object
            start = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
            current_time = acc.get_current_time()
            if (current_time > start and current_time < end):
                # we can send instructions to the drone
                mission_type = "takeoff"
                # we check the desired altitude
                if alt < max_alt:
                    input= {
                        "command":str(mission_type),
                        "service_key":key,
                        "altitude":alt
                    }

                    url="http://drone:5000/droneapi/v1/operations/takeoff"
                    try:
                        resp = requests.post(url,json=input)
                        resp.raise_for_status()
                    except requests.exceptions.HTTPError as httpErr:
                        print("httpError, mission request can be posted:", httpErr)
                    #get back the answer from the server
                    try :
                        result=resp.json()
                        time.sleep(0.0005)
                        # we check the status code
                        status_code = result['status_code']
                        if status_code == 200:
                            resp = {"status_code":200,
                                    "msg": "the drone is flying"
                            }
                    except (ValueError):
                        result = {"result":"json test error"}
                    resp = result
                    return jsonify(resp)

                else:
                    resp = {"status_code":402,
                            "msg": "operation denied,this key does not exist"
                    }


        else :
            resp = {"status_code":400,
                    "msg": "operation denied,this key does not exist"
            }
        return jsonify(resp)
        pass
class Goto(Resource):

    rf = api.model('goto',{
             'x':fields.Integer(description="desired x destination in meter "),
             'y':fields.Integer(description="desired y destination in meter "),
             'z':fields.Integer(description="desired fly altitude  in meter  "),
             'clearance': fields.String(description="Check the clearance in your mail")
    })

    @api.doc(responses={
        200: 'Success',
        400: 'operation denied,the key does not exist',
        401: 'operation denied,the key is no longer valid',
        402: 'operation denied,altitude too high,risk of coolision',
        403: 'This area is not availbale on the map',
        404: 'resticted area, operation denied',
        500: 'Internal server error'
    })

    @api.expect(rf,validate=True)
    def post(self):
        """ set a waypoint  """
        #resp = None
        #define room location
        r = room_location()
        #here we define where the drone can fly , only inside the cage
        g = r.set_covered_area(0.4,4,0.4,4)# global location
        goto_data = request.get_json()
        x = goto_data['x']
        y = goto_data['y']
        z = goto_data['z']
        clearance = goto_data['clearance']


        acc = AccreditationModel()
        req = acc.check_clearance(clearance)
        if  bool(req):
            """ the user can  send command only between a certain time  """
            s = req["start_time"]
            e = req["end_time"]
            # we convert the string into dattime object
            start = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
            current_time = acc.get_current_time()
            if (current_time > start and current_time < end):
                # we can send instructions to the drone
                mission_type = "goto"
                # we check the desired altitude
                if z < max_alt:
                    # we define a location using the coordinate
                    location = Point(x,y)

                    if location.within(covered_area):
                        if not location.within(restricted_zone):
                            resp = {
                                "status_code":200,
                                "msg":"the drone is flying to the destination"
                            }
                        else:
                            resp = {
                                "status_code":404,
                                "msg":'resticted area, operation denied',
                            }
                    else:
                        resp = {
                            "status_code":403,
                            "msg":'this area is not available on the map',
                        }


                    # if (x > g["x1"] and x <= g["x2"]*0.90 and y > g["y1"] and y <= g["y2"]*0.90 ):
                    #     print("we can fly to your destination")
                    #     resp = {"status_code":200,
                    #             "msg": "the drone is flying to the destination"
                    #     }
                    # else:
                    #     resp = {"status_code":403,
                    #             "msg": "this area is not available on the map"
                    #     }

                else:
                    resp = {"status_code":402,
                            "msg": "alititude too high"
                    }


            else :
                resp = {"status_code":400,
                        "msg": "operation denied,the key is no more valid"
                }
        else:
            resp = {"status_code":400,
                    "msg": "operation denied,the key does not exist"
            }

        return jsonify(resp)

class check_position:
    pass
Acc_api.add_resource(PreCheckFlight,'/clearance')
Mission_api.add_resource(Arming,'/arming')
Mission_api.add_resource(Takeoff,'/takeoff')
Mission_api.add_resource(Goto,'/goto')
