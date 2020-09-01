from aelab import app, api, login
from flask_login import current_user , login_user , logout_user ,login_required
from flask import render_template, url_for,flash, redirect, request, jsonify, flash, Blueprint, send_from_directory, send_file, Response
from flask_restful import Resource
from aelab.forms import RegistrationForm,LoginForm,DroneForm,AccreditationForm,ArmningForm,TakeoffForm,GotoForm
from aelab.models import UserRegModel,UserModel,DbModel,DroneModel
from aelab.camera import VideoCamera
from threading import Thread, Lock
import requests, json, time, os, threading

lock = Lock() # for handling the concurrency for accessing the camera
output_frame = None
vs = VideoCamera()



def gen():
    global vs, lock
    if vs == None:
        vs = VideoCamera()

    while True:
        with lock:
            data = vs.get_frame()
            frame = data[0]
            # use yield function instead of return
            if frame != None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/video_feed')
def video_feed():
    return Response( gen(), mimetype="multipart/x-mixed-replace; boundary=frame")



# index route for test the app
@app.route("/homepage")
def homepage():
    return render_template("home.html")

""" function for testing posted data """



""" Here we handle all about user registration  """
@app.route("/register", methods=['get','post'])
def register():
    usr=UserRegModel()
    form = RegistrationForm()
    if form.validate_on_submit():
        #get the data from the form
        email=form.email.data
        username=form.username.data
        password=form.password.data
        student_id=form.student_id.data
        #send the information to the web service
        register_data = {
            'email':email,
            'username': username,
            'password': password,
            'student_id':student_id
        }
        url = "http://webapi:5000/webapi/v1/user/register"
        try :
            resp = requests.post(url,json=register_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)

        #get back the answer from the server
        #and then send the parameter to the form

        try :
            result=resp.json()
            # if the result is sucessfull we need to register the mission to the db
            time.sleep(0.0005)
            if result['status_code'] !=200:
                msg = "try again,registration denied "
                return render_template('register.html', title='Sign Up', msg=msg, form=form)
            else:
                # the user is registerd
                msg = "the registration was successful, you can now log in "
                return render_template('register.html', title='Sign Up', msg=msg, form=form)


        except (ValueError):
            result = {"result":"json error"}

        #usr.add_user(email,username,password,student_id)
    return render_template('register.html', title='Sign Up',form=form)


""" Here we handle the login to access the different services of the platform  """

#creation of the load_user function to handle already logged in user
@login.user_loader
def load_user(user_id):
    dbmodel=DbModel()
    user_pwd=dbmodel.Document.data.find({"username":user_id},{"password":1})
    if user_pwd is not None:
        return UserModel(user_id)


@app.route('/login', methods=['get','post'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        # send to the the webapi_service
        login_data = {
            'username':username,
            'password':password
        }

        url = "http://webapi:5000/webapi/v1/user/login"
        try :
            resp = requests.post(url,json=login_data)
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


        if result['status_code'] == 200 :
            usr=UserModel(username)
            login_user(usr)
            return redirect(url_for('services'))
        else :
            return render_template('login.html', title='Sign In', form=form)

    return render_template('login.html', title='Sign In', form=form)

""" Here we handle the page after you are logged in  """
@app.route('/services',methods=['GET'])
@login_required
def services():
    username=current_user.username
    return render_template('services.html',username=username)

@app.route('/users')
@login_required
def get_all_user():
    if UserModel(current_user.username).get_user_role()=="admin":
        usr=UserRegModel()
        users=usr.get_users()
        return users
    else :
        return "you are not logged as admin "



@app.route('/users/<username>')
def get_user(username):
    usr=UserRegModel()
    #details=usr.get_user(username)
    details=usr.get_user_role(username)
    return details


""" Here we will handle the drone registration"""
@app.route('/drone_reg',methods=['get','post'])
@login_required
def drone_reg():
    form=DroneForm()
    drone_model=DroneModel()
    if form.validate_on_submit():
        #get the data from the form
        serial_number=form.serial_number.data
        name=form.name.data
        type=form.type.data
        flight_time=form.flight_time.data
        weight=form.weight.data
        span=form.span.data
        radius=form.radius.data
        max_alt=form.max_altitude.data
        # we insert them in the db
        drone_model.add_drone(serial_number,name,type,serial_number,weight,span,radius,max_alt)
        return render_template('drone_reg.html',message="do you want to add another drone!!!",form=form)
    return render_template('drone_reg.html',current_user=current_user,title='@elab drone registration',form=form)

@app.route('/accreditation',methods=['post','get'])
@login_required
def accreditation():
    form=AccreditationForm()
    drone_model=DroneModel()
    username=current_user.username
    dronesList=drone_model.get_all_drone()
    for drone in dronesList:
        form.type.choices.append( (drone['serial_number'],drone['name']) )
    if form.validate_on_submit():
        #get the data from the form
        date=form.date.data
        _date=str(date)
        hour=form.hour.data
        _hour=str(hour)
        duration=form.duration.data
        _duration=str(duration)

        # get the selected field
        index=form.type.data
        #get the value of the selected field
        selected_drone=dict(form.type.choices)[index]
        altitude=form.altitude.data
        radius=form.radius.data
        acc_data ={
            "username":current_user.username,
            "drone_name":selected_drone,
            "date":_date,
            "hour":_hour,
            "duration":_duration,
            "altitude":altitude,
            "radius":radius
        }
        url="http://controller:5000/middleapi/clearance"
        try :
            resp = requests.post(url,json=acc_data)
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
        return render_template('accreditation.html',form=form,drones=dronesList,result=result,username=username)
    return render_template('accreditation.html',form=form,drones=dronesList,username=username)

@app.route('/template')
def template():
    return render_template('basic_bootstrap.html')

@app.route('/missions',methods=['GET','POST'])
@login_required
def missions():
    username=current_user.username
    arming_form = ArmningForm()
    takeoff_form = TakeoffForm()
    goto_form = GotoForm()
    if arming_form.validate_on_submit() and "arm" in request.form:
        msg="arm"
        #get the mission command and send it to the server
        mission_type = request.form.get('arm')
        #create the json data to send to the server
        arming_data = {
            "username":current_user.username,
            "clearance":arming_form.credential.data
        }
        # we send the request to the controller service
        url="http://controller:5000/middleapi/arming"
        try:
            resp = requests.post(url,json=arming_data)
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
            result = {"msg":"internal server error"}
        return render_template('missions.html',username=username,arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,msg=result)


    elif takeoff_form.validate_on_submit() and "takeoff" in request.form:
        msg="set the alt for taking off "
        mission_type = request.form.get('takeoff')
        #create the json data to send to the server
        takeoff_data = {
            "username":current_user.username,
            "altitude":takeoff_form.alt.data,
            "clearance":takeoff_form.credential.data,
            "mission_type":mission_type
        }
        # we send the request to the server
        url="http://controller:5000/middleapi/takeoff"
        try:
            #req_data = json.dumps(input)
            resp = requests.post(url,json=takeoff_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            time.sleep(0.0005)
        except (ValueError):
            result = {"msg":"internal server error"}
        return render_template('missions.html',username=username,arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,msg=result)

    elif goto_form.validate_on_submit() and goto_form.validate():
        msg="set the lat, long and alt "
        #create the json data to send to the server
        goto_data = {
            "username":current_user.username,
            "mission_type":request.form.get('goto'),
            "x":goto_form.lat.data,
            "y":goto_form.long.data,
            "z":goto_form.alt.data,
            "clearance":goto_form.credential.data
        }
        # we send the request to the server
        url="http://controller:5000/middleapi/goto"
        try:
            resp=requests.post(url,json=goto_data)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try:
            result=resp.json()
            time.sleep(0.0005)
        except (ValueError):
            result = {"msg":"internal server error "}

        return render_template('missions.html',username=username,arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,msg=result)

    else:
        return render_template('missions.html',arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,username=username)


@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.username

#the logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/file_downloads')
def return_file():
    return send_file("templates/services.html",as_attachment=True)
