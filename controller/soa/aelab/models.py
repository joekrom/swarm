from aelab import mail
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps,loads
from datetime import datetime, timedelta
from flask_mail import Message
import json, uuid
import pytz


class DbModel:
    def __init__(self):
        #make the connection to the db
        try:
            client = MongoClient('mydb',27017)
        except ConnectionFailure:
            print("server not available")
    #create or access the database
        self.Document=client.mydb

class AccreditationModel:
    def __init__(self):
        dbmodel=DbModel()
        self.col_users=dbmodel.Document.users
        self.col_drones=dbmodel.Document.drones

    def get_accreditation_list(self):
        #this query allow us to check all list
        # we are checking an array with one element
        acc_lists=self.col_users.find({"accreditations": {"$size":1}})
        return acc_lists
    def add_accreditation(self,username,drone_name,credential,date,start_time,end_time):
        self.col_users.update_one(
            {"username":username},
            {"$push":
                {"accreditations":
                    {"$each":
                        [
                            {
                                "username":username,
                                "drone_name":drone_name,
                                "credential":credential,
                                "date":date,
                                "start_time":start_time,
                                "end_time":end_time
                            }
                        ]
                    }
                }
            }
        )
    def get_date(self,username):
        # this function will help us get an element in an array
        cursor=self.col_users.find({"usernanme":username},{"_id":0,"accreditations.date":1})
        json_str=dumps(cursor)
        rs=loads(json_str)
        # the result is a dictionary
        return rs

    def get_all_accreditions_time(self):
        cursor=self.col_users.find({},{"_id":0,"accreditations.date":1})
        json_str=dumps(cursor)
        rs=loads(json_str)
        # the result is a list of dictionaries
        return rs

    def get_acc_per_date(self,date):
        # dont forget the . to access the subdocument get the date , the start_time and the end_time
        filter="accreditations." + date
        cursor=self.col_users.find({"accreditations.date":date},{"_id":0,"accreditations.date":1,"accreditations.start_time":1,"accreditations.end_time":1})
        json_str=dumps(cursor)
        rs=loads(json_str)
        # the result is a list of dictionaries
        return rs
    def get_current_time(self):
        # first we get the UTC time
        utcnow = datetime.now(tz=pytz.UTC)
        # Now we retrieve the aware time
        dtnow =  utcnow.astimezone(pytz.timezone('Europe/Berlin'))
        # we transfor the current time into string
        dtstr = str(dtnow)
        # Now we create a naive datetime obj
        dt = dtstr.split('.')[0]
        current_time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        return current_time


    def check_clearance(self,acc):
        # we retrive the list with the credential to retrieve the one we need
        cursor = self.col_users.find({"accreditations.credential":acc},{"_id":0,"accreditations.credential":1,"accreditations.start_time":1,"accreditations.end_time":1})
        json_str=dumps(cursor)
        rs=loads(json_str)
        # the result is a list of dictionaries
        try:
            dict = rs[0].get("accreditations")
            for elem in dict :
                if elem["credential"] == acc:
                    dict = elem
                    break
        except (IndexError):
            dict = {}
        return dict

    def credential_key(self):
        # function that generates and returns a unique credentail number
        key = uuid.uuid4()
        credential = str(key)
        return credential

    def send_credential(self,email,credential):
        msg = Message(
          '@elabservice',
           sender='user@gmail.com',
           recipients=[str(email)]
        )
        msg.body = "this is your clearance key :" + credential
        mail.send(msg)

    def flight_approval(self,input):
        #input data we get from the form , now we retrieve data from the form
        radius = int(input['radius'])
        altitude = int(input['altitude'])
        username = str(input['username'])
        drone_name = str(input['drone_name'])
        duration = int(input['duration'])
        date = str(input['date'])
        hour = str(input['hour'])
        #we concatenate the date an hour to get a datetime string
        start_time = date+" "+hour
        # we create the datetime object
        start_time_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time_obj = start_time_obj+ timedelta(minutes=duration)
        end_time = end_time_obj.strftime('%Y-%m-%d %H:%M:%S')


        answer = {"result":"there is no free time slot"}
        free_time_slot = False # boolean variable for checking if there is free time slot

        #we first check if the flight plan of the user
        if ( (altitude > 3) or  (radius > 5) ):
            answer = {"result":"The flight plan was not approved,retry",
                      "message": "accrediation denied, flight parameter not accepted",
                      "status_code": 401
            }
            return answer
        else :
            # we check if date is in the past
            now = self.get_current_time()
            if start_time_obj < now:

                answer={
                    "result":"invalid information",
                    "message":"inaccurate data",
                     "status_code": 405
                }
                return answer

            #we check if there is a free  time slot
            # we get the accreditations list of the input date
            Accreditations = self.get_acc_per_date(date)
            #we check if the accreditations list for one day is empty
            if len(Accreditations) == 0:
                free_time_slot = True
            else:
                # the list is not empty
                #we check if the intersection is empty
                for dictlist in Accreditations:
                    # we get accretation list of each dictionaries in the list
                    acc_list = dictlist.get("accreditations")
                    if ( len(acc_list) !=0 ):
                        # then we loop the list of each accreditation in that subdocument
                        for acc in acc_list:
                            # ac is a dictionary
                            # now we retrieve the required data from the dict
                            #s is for start_time and e is for end_time
                            s=str(acc.get("start_time"))
                            e=str(acc.get("end_time"))
                            #we convert the object to datetime object
                            s_db=datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                            e_db=datetime.strptime(e, '%Y-%m-%d %H:%M:%S')
                            #access={"result":str(this_list)}
                            #then we make the comparison with the actual request
                            if ( (start_time_obj > e_db ) or (s_db > end_time_obj) ) != True:
                                # there is no intersection
                                free_time_slot = False
                                answer={"result":"this slot is no more available",
                                        "message": "time slot already reserved",
                                        "status_code":402
                                }
                                break
                            else:
                                free_time_slot = True

                    if free_time_slot == False:
                        break
        # At last we check the free_time_slot and insert data in the db
        if free_time_slot:
            # we generate the credential
            credential = self.credential_key()
            #we send request to the db
            self.add_accreditation(username,drone_name,credential,date,start_time,end_time)
            # retrive the email of the user and then config a SMTP EMAIL
            # we send the email using the email corresponding to username
            self.send_credential("joel.dfankam@yahoo.fr",credential)
            answer={"result":"this slot is free, check your email",
                    "message":"accredition approved, check your mail to get the key ",
                    "status_code":200
            }

        return answer

class MissionModel:
    # this class will allow us to handle
    pass
