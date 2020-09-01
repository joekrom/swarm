from aelab import app, mail #, auto

from flask import render_template, url_for,flash, redirect, request, jsonify, json, abort
from datetime import datetime, timedelta
from flask_mail import Message
from aelab.models import AccreditationModel
import uuid,requests,json,time

quarks = [{'name': 'up', 'charge': '+2/3'},
          {'name': 'down', 'charge': '-1/3'},
          {'name': 'charm', 'charge': '+2/3'},
          {'name': 'strange', 'charge': '-1/3'}]


""" tests  with requests """

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'Hello, World!'})

@app.route('/quarks', methods=['GET'])
def returnAll():
    return jsonify({'quarks' : quarks})

@app.route('/quarks/<string:name>', methods=['GET'])
def returnOne(name):
    theOne = quarks[0]
    for i,q in enumerate(quarks):
      if q['name'] == name:
          theOne = quarks[i]
    return jsonify({'quarks' : theOne})

@app.route('/quarks', methods=['POST'])
def addOne():
    new_quark = request.get_json()
    quarks.append(new_quark)
    return jsonify({'quarks' : quarks})

@app.route('/quarks/<string:name>', methods=['PUT'])
def editOne(name):
    new_quark = request.get_json()
    for i,q in enumerate(quarks):
      if q['name'] == name:
        quarks[i] = new_quark
    qs = request.get_json()
    return jsonify({'quarks' : quarks})

@app.route('/quarks/<string:name>', methods=['DELETE'])
def deleteOne(name):
    for i,q in enumerate(quarks):
      if q['name'] == name:
        del quarks[i]
    return jsonify({'quarks' : quarks})

""" end test """



# index route for test the app
@app.route("/index")
def index():
    return render_template("base.html")

@app.route("/server", methods=['post'])
def server():
    data=request.get_json()
    x1=data["x"]
    y1=data["y"]
    sum=0
    x=0
    y=0
    x=int(x1)
    y=int(y1)
    sum=x+y
    result={"sum":sum}
    return result
    #return jsonify(result)

# to generate the documentation page
"""@app.route('/documentation')
def documentation():
    return auto.html()"""

@app.route("/accreditation",methods=['post'])
#@auto.doc()
def accredition():
    data=request.get_json()
    acc_model=AccreditationModel()
    return acc_model.flight_approval(data)

@app.route("/missions_reg",methods=['post','get'])
def missions_reg():
    answer = {"result":"default"}
    # first we get the data form the request
    mission_type=""
    data = request.get_json()
    #we retrieve the type of mission
    #mission_type = json.loads(data)['mission_type']
    mission_type = request.args.get('mission_type')
    if (mission_type == 'arm'):
        # for arming
        #answer = {"result":"your are request is valid,the drone is arming"}
        #check the accreditation and the time
        #we make a call to the drone service
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

        answer = result

    if (mission_type == 'takeoff'):
        # we do some verifications, make the ops and send the response
        #answer = {"result":"takeoff, your are request is valid"}
        # for taking off
        #check the accredition
        """ if the verifications are successfull,the request can then
        to the drone service """
        #alt = json.loads(data)['altitude']
        alt = request.args.get('altitude')
        input = {"alt":alt}
        #we send the request to the drone service
        url="http://dronekit:5000/go_to_alt"
        try:
            #resp = requests.post(url,json=input)
            #req_data = json.dumps(input)
            resp = requests.post(url,params=input)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("httpError, mission request can be posted:", httpErr)
        #get back the answer from the server
        try :
            result=resp.json()
            #time.sleep(0.0005)
        except (ValueError):
            result = {"result":"json test error"}

        answer = result

    if (mission_type == 'goto'):
        # we do some verifications, make the ops and send the response
        answer = {"result":"goto, your are request is valid"}
    return answer















































    # # get the data
    # access={}
    # # we suppose there is a free time space
    # # we will also check the inner loop with it
    # check_free_time=True
    # data=request.get_json()
    # radius=int(data['radius'])
    # username=str(data['username'])
    # drone_name=str(data['drone_name'])
    # duration=int(data['duration'])
    # date=str(data['date'])
    # hour=str(data['hour'])
    # start_time=date+" "+hour
    # #create a datetime object
    # start_time_obj=datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    # end_time_obj=start_time_obj+ timedelta(minutes=duration)
    # end_time=end_time_obj.strftime('%Y-%m-%d %H:%M:%S')
    #
    # acc_model=AccreditationModel()
    # # we will make multiple condition for the flying pre-check
    # if radius < 5:
    #     #we check if the accreditions list of the day is empty
    #     if len( acc_model.get_acc_per_date(date) )==0:
    #         # generate a unique number with the uuid library
    #         acc_number=uuid.uuid4()
    #         credential=str(acc_number)
    #         #add the credential in the users document
    #         acc_model.add_accreditation(username,credential,date,start_time,end_time)
    #         msg = Message(
    #           'Hello',
    #            sender='user@gmail.com',
    #            recipients=
    #            ['joel.fankam@gmail.com'])
    #         msg.body = credential
    #         mail.send(msg)
    #         access={"result":"the list of the day is empty"}
    #
    #     else:
    #         # the list is not empty
    #         access={"result":"the list of the day  is not empty"}
    #         Accreditations=acc_model.get_acc_per_date(date)
    #         this_list=[]
    #         for diclist in Accreditations:
    #             acc_list=diclist.get("accreditations")
    #             if (  len(acc_list)!=0 ):
    #                 # then i loop the list of each accrediation in that subdocument
    #                 for acc in acc_list:
    #                     # ac is a dictionary
    #                     # now we retrieve the required data from the dict
    #                     #s is for start_time and e is for end_time
    #                     s=str(acc.get("start_time"))
    #                     e=str(acc.get("end_time"))
    #                     #we convert the object to datetime object
    #                     s_db=datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    #                     e_db=datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
    #                     this_list.append(e_db)
    #                     #access={"result":str(this_list)}
    #                     #then we make the comparison with the actual request
    #                     if ( (start_time_obj > e_db ) or (s_db > end_time_obj) ) != True:
    #                         #is there is an intersection
    #                         access={"result":"this time slot is no more avaible"}
    #                         check_free_time=False
    #                         break
    #                     # else:
    #                     #      #is there is no intersection
    #                     #      access={"result":"there is no intersection"}
    #                     #      check_free_time=True
    #             if check_free_time == False:
    #                 break
    #
    #         if check_free_time:
    #             access={"result":"time slot is free , insert data in db and send credential"}
    #             #acc_model.add_accreditation(username,credential,date,start_time,end_time)
    # else:
    #     access={"result":"you failed the pre-check-flight"}
    #
    # return access
