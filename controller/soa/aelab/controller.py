from aelab import app, mail, api

from flask import render_template, url_for,flash, redirect, request, jsonify, json, abort
from datetime import datetime, timedelta
from flask_mail import Message
from flask_restplus import Resource, fields, Namespace
from aelab.models import AccreditationModel
from datetime import datetime, timezone
import uuid,requests,json,time
import pytz

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
        credential_data = request.get_json()
        date = credential_data['date']
        hour = credential_data['hour']
        duration = credential_data['duration']
        status_code = self.checkformat(hour,duration,date)
        # check if the username exist and drone exist
        # check if time is not < to the time at the request

        if (status_code != 400 ):
            # we handle the request
            acc_model=AccreditationModel()
            try:
                rs = acc_model.flight_approval(credential_data)
                status_code = rs["status_code"]
                message = "check your clearance in your emails"
            except:
                status_code = 500
                message = "Check your inputs """

        resp = {"status_code":status_code}
        return jsonify(resp)

class Arming(Resource):

    rf = api.model('arming',{
             'clearance': fields.String(description="Check the clearance in your mail")
    })
    @api.expect(rf,validate=True)
    def post(self):
        """ Arm a drone """
        mission_data = request.get_json()
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

                input = {"command":str(mission_type)}
                # we send the request to the drone
                url="http://dronekit:5000/arm"
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
                return {"message":"your clearance is no more usable",
                        "time": str(req)
                }

            return jsonify({"message":str(datetime.now())})
        else :
            status_code = 400
            return jsonify({"type":"nothing"})

class Takeoff(Resource):

    rf = api.model('takeoff',{
             'altitude': fields.Integer,
             'clearance': fields.String(description="Check the clearance in your mail")
    })
    @api.expect(rf)
    def post(self,validate=True):
        """ fly the drone to a defined altitude  """
        pass
class Goto(Resource):

    rf = api.model('goto',{
             'x':fields.Integer(description="desired x destination in meter "),
             'y':fields.Integer(description="desired y destination in meter "),
             'z':fields.Integer(description="desired fly altitude  in meter  "),
             'clearance': fields.String(description="Check the clearance in your mail")
    })
    @api.expect(rf,validate=True)
    def post(self):
        """ set a waypoint  """
        pass

Acc_api.add_resource(PreCheckFlight,'/clearance')
Mission_api.add_resource(Arming,'/arming')
Mission_api.add_resource(Takeoff,'/takeoff')
Mission_api.add_resource(Goto,'/goto')
