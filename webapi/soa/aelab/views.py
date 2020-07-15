from aelab import app, api, login
from flask_login import current_user , login_user , logout_user ,login_required
from flask import render_template, url_for,flash, redirect, request, jsonify, flash, Blueprint
from flask_restful import Resource
from aelab.forms import RegistrationForm,LoginForm,DroneForm,AccreditationForm,ArmningForm,TakeoffForm,GotoForm
from aelab.models import UserRegModel,UserModel,DbModel,DroneModel
from threading import Thread
import requests,json,time

# Prefix all URLs
bp = Blueprint('bp', __name__)

# index route for test the app
@app.route("/homepage")
#@bp.route("/homepage")
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
        #send the information to the database
        usr.add_user(email,username,password,student_id)
        return redirect(url_for('homepage'))

    return render_template('register.html', title='Sign Up', form=form)


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
        usr=UserModel(username)
        if usr.check_username(username):
            password=form.password.data
            if usr.check_access(username,password):
                login_user(usr)
                return redirect(url_for('services'))
            else:
                return render_template('login.html', title='Sign In', form=form)
        else:
            render_template('login.html', title='Sign In', form=form)
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
        drone_model.add_drone(serial_number,model,type,serial_number,weight,span,radius,max_alt)
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
        hour=str(hour)
        duration=form.duration.data
        # get the selected field
        index=form.type.data
        #get the value of the selected field
        selected_drone=dict(form.type.choices)[index]
        altitude=form.altitude.data
        radius=form.radius.data
        input ={
            "username":current_user.username,
            "drone_name":selected_drone,
            "date":_date,
            "hour":hour,
            "duration":duration,
            "altitude":altitude,
            "radius":radius
        }
        url="http://aelab_server:5000/accreditation"
        #url="http://192.168.178.160:4003/accreditation"
        resp=requests.post(url,json=input)
        result=resp.json()
        time.sleep(0.0005)
        return render_template('accreditation.html',form=form,drones=dronesList,result=result)
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
        input = {
            "username":current_user.username,
            "credential":arming_form.credential.data,
            "mission_type":request.form.get('arm')
        }
        # we send the request to the server
        url="http://aelab_server:5000/missions_reg"
        #url= "http://192.168.178.160:4003/missions_reg"
        try:
            resp = requests.post(url,params=input)
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
        return render_template('missions.html',username=username,arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,msg=result)

    if takeoff_form.validate_on_submit() and "takeoff" in request.form:
        msg="set the alt for taking off "
        mission_type = request.form.get('takeoff')
        #create the json data to send to the server
        input = {
            "username":current_user.username,
            "altitude":takeoff_form.alt.data,
            "credential":takeoff_form.credential.data,
            "mission_type":mission_type
        }
        # we send the request to the server
        url="http://aelab_server:5000/missions_reg"
        try:
            #req_data = json.dumps(input)
            resp = requests.post(url,params=input)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json error"}
        return render_template('missions.html',username=username,arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,msg=result)

    if goto_form.validate_on_submit() and "goto" in request.form:
        msg="set the lat, long and alt "
        #create the json data to send to the server
        input = {
            "username":current_user.username,
            "credential":arming_form.credential.data,
            "mission_type":request.form.get('goto')
        }
        # we send the request to the server
        url="http://aelab_server:5000/missions_reg"
        try:
            resp=requests.post(url,json=input)
            resp = requests.post(url,params=input)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        #and then send the parameter to the form
        try :
            result=resp.json()
            time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json error"}
        return render_template('missions.html',username=username,arming_form=arming_form,takeoff_form=takeoff_form,goto_form=goto_form,msg=result)


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

@app.route('/mission_test', methods=['get','post'])
def mission_test():
    form = MissionForm()
    if form.validate_on_submit():


        # get and test the selected  field mission
        #index=form.mission.data
        #return render_template('missions.html',form=form)
        return render_template('base.html')
    return render_template('mission_test.html',form=form)


# define the ressources for the views
class Test(Resource):
    #form=RegistrationForm()
    def get(self):
        return render_template('home.html' )
    """def post(self):
        pass"""


""" here we will testing the client server between services  """

shared_var = None

def send_post_req(url,data):
    global shared_var
    resp=requests.post(url,json=data)
    shared_var=resp.json()

class Client(Resource):
    def post(self):
        req_counter=0
        posted_data=request.get_json()
        x1=posted_data["x"]
        y1=posted_data["y"]
        x=int(x1)
        y=int(y1)
        input={"x":x,"y":y}
        #url="http://139.174.107.26:5000/server"
        """ we can replace the name of ip with the name of the service  """
        url="http://aelab_server:4003/server"
        """t = Thread(target=send_post_req, args=(url, input))
        t.setDaemon(True)
        t.start()
        time.sleep(0.05)
        return jsonify(shared_var)"""

        resp=requests.post(url,json=input)
        time.sleep(0.0005)

        return str(resp.content)

#define the route for the resources
#api.add_resource(Test, '/test')
#api.add_resource(Client,'/client')
