from pymongo import MongoClient
from flask_login import UserMixin
from bson.json_util import dumps,loads
from flask import jsonify,json
import json, pymongo



class DbModel:
    def __init__(self):
        #make the connection to the db
        client=MongoClient('mydb',27017)
        #create or access the databaase
        self.Document=client.mydb

class UserRegModel:
    def __init__(self):
        dbmodel=DbModel()
        #self.col=dbmodel.Document.data
        self.col=dbmodel.Document.users


    def add_user(self,email,username,password,student_id):
        self.col.insert_one({
            "email":email,
            "username":username,
            "password":password,
            "student_id":student_id,
            "role":"user",
            "accreditations":[],
            "drones":[]
        })

    def get_users(self):
        #rs=self.db.data.find({},{"_id":0,"password":0})
        rs=self.col.find({},{"_id":0})
        json_str=dumps(rs)
        ret_json=loads(json_str)
        return jsonify(ret_json)

    def get_user(self,username):
        rs=self.col.find({"username":username},{"_id":0,"password":0})
        json_str=dumps(rs)
        d=json.loads(json_str)
        # d is a list and we can access its element
        return jsonify(d[0])

    def get_user_role(self,username):
        rs=self.col.find({"username":username},{"_id":0,"role":1})
        json_str=dumps(rs)
        d=json.loads(json_str)
        # d is a list and we can access its element
        return str(d[0]["role"])
        
    def add_mission(self,mission_type):
        pass





class UserModel(UserMixin):
    def __init__(self,username):
        self.username=username
        #make the connection to the db
        client=MongoClient('mydb',27017)
        #create or access the databaase
        self.db=client.mydb

    #this function helps us to get username from the db
    def check_username(self,username):
        checked=False
        rs=self.db.users.find_one({"username":username},{"username":1})
        if rs is not None:
            checked=True
        else:
            checked=False
        return checked
    #then we check the password only if the username is in the db
    def check_access(self,username,password):
        access=False
        rs=self.db.users.find_one({"username":username,"password":password})
        if rs is not None:
            access=True
        else:
            access=False
        return access

    def get_user_role(self):
        rs=self.db.users.find({"username":self.username},{"_id":0,"role":1})
        json_str=dumps(rs)
        d=json.loads(json_str)
        # d is a list and we can access its element
        return str(d[0]["role"])

    # the get_id method returns a unique identifier for a user
    def get_id(self):
        return self.username

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

class DroneModel:
    def __init__(self):
        dbmodel=DbModel()
        #self.col=dbname.Document.data
        dbmodel.Document.drones.create_index([("serial_number",pymongo.ASCENDING)],unique=True)
        self.col=dbmodel.Document.drones

    def add_drone(self,serial_number,name,type,flight_time,weight,span,radius,max_alt):
        self.col.insert_one({
            "serial_number":serial_number,
            "name":name,
            "type":type,
            "flight_time":flight_time,
            "weight":weight,
            "span":span,
            "radius":radius,
            "max_alt":max_alt,
            "availability":True,
            "users":[]
        })
    def get_all_drone(self):
        rs=self.col.find({},{"_id":0})
        # the result is a cursor object
        json_str=dumps(rs)
        drones=json.loads(json_str)
        return drones




    # this is how to update
    """def add_drone(self,name,type,serial_number,weight,span,radius,max_alt):
        #first we create a drones in the document if it does not exist
        self.col.update_one({"username":operator},
            {"$set":
                {"drones":[]}
            }
        # now we update the doc with the data
        self.col.update_one({"username":operator},
            {"$push":
                {"drones":
                    {"$each":
                        [
                           {
                            "operator":operator,
                            "name":name,
                            "type":type,
                            "serial_number":serial_number,
                            "weight":weight,
                            "span":span,
                            "radius":radius,
                            "max_alt":max_alt
                            }
                        ]
                    }
                }
            }
        )"""
