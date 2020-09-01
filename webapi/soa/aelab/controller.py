"Here we will expose our services"
from aelab import  api, login #app
from flask_login import current_user , login_user , logout_user ,login_required
from flask import render_template, url_for,flash, redirect, request, jsonify, flash, Blueprint
#from flask_restful import Resource
#from flask_restplus import Resource
from flask_restplus import Resource, fields, Namespace
from aelab.models import UserRegModel,UserModel,DbModel,DroneModel
from threading import Thread
import requests,json,time

#api = Namespace('User', description='User related operations')
users_api = Namespace('users')
admin_api = Namespace('admin')
mission_api = Namespace('Missions')
api.add_namespace(users_api,path='/webapi/v1/user')
api.add_namespace(admin_api,path='/webapi/v1/admin')
api.add_namespace(mission_api,path='/webapi/v1/mission')
class Home(Resource):
    @login_required
    def get(self):
        return {"hey":"there"}


""" Route handling the registration using the api """


class Sign_in(Resource):
    rf1 = api.model('sign_in', {
        'email': fields.String,
        'username': fields.String,
        'password': fields.String,
        'student_id': fields.String,
    })

    @api.doc(responses={
        200: 'Success',
        401: 'Validation Error',
        402: 'missing value',
        403: 'bad email',
        500: 'Bad request'
    })
    @api.expect(rf1,validate=True)
    def post(self):
        """
            Allow users to register themselves
        """
        #if the ressource register was requested using the method post
        try :
            register_data = request.get_json()
            # we check the poseted_data
            # we get the data from the dictionary
            email = register_data["email"]
            username = register_data["username"]
            password = register_data["password"]
            student_id = register_data["student_id"]
            # check if the email is valid
            test_email = email[-10:]# with this line we get the 10 last character
            if test_email == "@gmail.com":
                # we add the register data in the db
                usr=UserRegModel()
                usr.add_user(email,username,password,student_id)
                # we formulate the response
                status_code = 200
            else:
                status_code = 403

            resp = {
                "status_code": status_code
            }
            return jsonify(resp)
        except (ValueError) :
            status_code = 401
            resp = {
                "Message":"something is missing",
                "status_code": status_code
            }
            return jsonify(resp)



#creation of the load_user function to handle already logged in user
@login.user_loader
def load_user(user_id):
    dbmodel=DbModel()
    user_pwd=dbmodel.Document.data.find({"username":user_id},{"password":1})
    if user_pwd is not None:
        return UserModel(user_id)




class Login(Resource):
    rf2 = api.model('logindata', {
        'username': fields.String,
        'password': fields.String,
    })
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error',
        301: 'wrong password ',
        302: 'wrong username'
    })
    @api.expect(rf2,validate=True)
    def post(self):
        try:
            login_data = request.get_json()
            username = login_data["username"]
            password = login_data["password"]
            usr=UserModel(username)
            if usr.check_username(username):
                if usr.check_access(username,password):
                    login_user(usr)
                    status_code = 200
                    resp = {
                        "Message":"you are logged in ",
                        "status_code": status_code
                    }
                    return jsonify(resp)
                else:
                    status_code = 301
                    resp = {
                        "Message":"pasword is wrong",
                        "status_code": status_code
                    }
                    return jsonify(resp)
            else:
                status_code = 302
                resp = {
                    "Message":"try another username",
                    "status_code": status_code
                }
                return jsonify(resp)

        except (ValueError) :
            status_code = 400
            resp = {
                "Message":"something is missing",
                "status_code": status_code
            }
            return jsonify(resp)


class UserList(Resource):
    def get(self):
        """
        Get the list of all user
        """
        return {"hey":"there"}


class Add_drone(Resource):
    def post(self):
        """
            Allow the admin to add a drone in the db
        """
        return {"hey":"there"}

    def delate(self,drone_id):
        """
            Allow to delate a drone from the db
        """

class GetDroneList(Resource):
    def get(self):
        """
        Allow to get the list of drone
        """
        return {"hey":"there"}

class Accreditation(Resource):
    rf1 = api.model('credential', {
        'username': fields.String,
        'drone_name': fields.String,
        'date': fields.String(description="date with format yyyy-mm-dd"),
        'duration':fields.String(description="%MM"),
        'hour':fields.String(description="%HH:%MM:%SS"),
        'altitude':fields.Integer,
        'radius':fields.Integer
    })

    @api.doc(responses={
        200: 'Success',
        400: 'error format time data',
        500: 'Bad request'
    })

    @api.expect(rf1)
    #@login_required
    def post(self):
        """
        Allow to make a request to get acrreditation for a time flight
        to the service controller
        """
        credential_data = request.get_json()
        # we send the request to the server
        url="http://aelab_server:5000/middleapi/clearance"

        try:
            resp = requests.post(url,json=credential_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            # if the result is sucessfull we need to register the mission to the db
            time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json error"}

        return jsonify(result)

class AccreditationList (Resource):
    def get(self):
        """
        Allow to make a request to get acrreditation for a time flight
        """
        return {"hey":"there"}

class RemoveAccreditation(Resource):
    def delete(self,username):
        """
        Allow to cancel credential
        """

class Geofencing(Resource):
    def post(self):
        """setting a Fence """
        return {"hey":"create a geofencing zone"}


class Arming(Resource):

    rf = api.model('arming',{
             'clearance': fields.String(description="Check the clearance in your mail")
    })
    @api.expect(rf,validate=True)
    def post(self):
        """ Arm a drone """
        mission_data = request.get_json()
        # we send the request to the server
        url="http://aelab_server:5000/middleapi/arming"

        try:
            resp = requests.post(url,json=mission_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            # if the result is sucessfull we need to register the mission to the db
            time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json error"}

        return jsonify(result)

class Takeoff(Resource):

    rf = api.model('takeoff',{
             'altitude': fields.Integer,
             'clearance': fields.String(description="Check the clearance in your mail")
    })
    @api.expect(rf)
    def post(self,validate=True):
        """ fly the drone to a defined altitude  """
        """ Arm a drone """
        mission_data = request.get_json()
        # we send the request to the server
        url="http://aelab_server:5000/middleapi/takeoff"

        try:
            resp = requests.post(url,json=mission_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            # if the result is sucessfull we need to register the mission to the db
            time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json error"}

        return jsonify(result)

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
        """ Arm a drone """
        mission_data = request.get_json()
        # we send the request to the server
        url="http://aelab_server:5000/middleapi/goto"

        try:
            resp = requests.post(url,json=mission_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            # if the result is sucessfull we need to register the mission to the db
            time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json error"}

        return jsonify(result)

#define the route for the resources
api.add_resource(Home,'/webapi/v1/homepage')
users_api.add_resource(Sign_in,'/register')
users_api.add_resource(Login,'/login')
users_api.add_resource(Accreditation,'/accreditation')
mission_api.add_resource(Arming,'/arming')
mission_api.add_resource(Takeoff,'/takeoff')
mission_api.add_resource(Goto,'/goto')
admin_api.add_resource(GetDroneList,'/drones')
admin_api.add_resource(Add_drone,'/add_drone')
admin_api.add_resource(UserList,'/users')
admin_api.add_resource(AccreditationList,'/accreditations')
admin_api.add_resource(RemoveAccreditation,'/rmvacc')
admin_api.add_resource(Geofencing,'/set_geofencing')
