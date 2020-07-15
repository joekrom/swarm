from dronekit import connect ,VehicleMode,LocationGlobalRelative
from flask import Flask, request, jsonify
import time,socket,threading,json

# global varaibale that will be use for handling the drone object

drone=None
# list of mode that are enabled
modes_list=[
    'STABILISE',
    'GUIDED',
    'LOITER',
    'RTL'
]

class Drone:
    def __init__(self,vehicle):
        self.vehicle = vehicle

    def set_vehicle_mode(self,mode):
        self.vehicle.mode=VehicleMode(mode)
        time.sleep(1)
        return "vehicle mode changed with success"

    def get_vehicle(self):
        return self.vehicle
    def get_system_status(self):
        return self.vehicle.system_status.state

    def get_std_info(self):
        pass

    def get_state(self):
        self.state['system_status']=str(self.get_system_status())
        self.state['alt']=str(self.get_altitude())
        self.state['long']=str(self.get_longitude())
        self.state['lat']=str(self.get_latitude())
        self.state['location']=str(self.get_location())
        return self.state

    def get_location(self):
        return self.vehicle.location.global_relative_frame

    def get_longitude(self):
        return self.vehicle.location.global_relative_frame.lon

    def get_latitude(self):
        return self.vehicle.location.global_relative_frame.lat

    def get_altitude(self):
        return self.vehicle.location.global_relative_frame.alt

    def get_vehicle_mode(self):
        return self.vehicle.mode.name

    #command to send to the vehicle
    def arm_disarm_vehicle(self,value):
        if not self.vehicle.armed and value :
            if not self.vehicle.is_armable:
                print("waiting for vehicle to be armable")
                print("arming motors")
                self.vehicle.armed=True
            while not self.vehicle.armed:
                print("wait for aming to take effect ")
                time.sleep(1)
            return "vehicle is armed"
        elif value:
            print("vehicle is already armed")
            return "vehicle is already armed"
        else:
            print("disarming motors ")
            self.vehicle.armed=False
            while self.vehicle.armed:
                print("waiting for disarming to trake effect ")
                time.sleep(1)
            return "vehicle is disarmed"

    def go_to_alt(self,alt):
        #arm the vehilce
        print("basic pre-arm checks ")
        #dont arm until the autopilot is ready
        while not self.vehicle.is_armable:
            print("waiting for vehicle to initialize")
            time.sleep(1)
        print("arming motors")
        #copter should arm in GUIDED mode
        self.vehicle.mode=VehicleMode("GUIDED")
        time.sleep(1)
        self.vehicle.armed=True
        time.sleep(1)

        #confirm vehicle is armed before attempting to take off
        while not self.vehicle.armed:
            print("waiting for arming")
            time.sleep(1)
        print("take off")
        self.vehicle.simple_takeoff(alt)# takeoff to a target altitude
        # wait until the vehicle reaches a safe height before processing the goto
        #otherwise the the command
        #after vehicle_takeoff will execute immediately
        while True :
            print("altitude: ",self.get_altitude())
            print("velocity: ",self.vehicle.velocity)
            print("battery: ",self.vehicle.battery)
            #break and return from function just below target altitude
            if self.get_altitude()>=alt*0.95:
                print("reached a target altitude")
                break
            time.sleep(1)
        # Hover for 10 seconds
        time.sleep(10)
        print("now let us land ")
        self.vehicle.mode=VehicleMode("RTL")
        time.sleep(1)
        self.vehicle.close()

app = Flask(__name__)
app.secret_key="dronekit"
# Threads that will be used to handle some request
t1=None

@app.before_first_request
def func():
    global drone
    try :
        #drone=Drone( connect('tcp:139.174.110.148:5760', wait_ready=True ) )
        drone=Drone( connect('udp:172.28.0.4:14553',wait_ready=True) )
        print("before_first_request is running connection successfull")
        time.sleep(5)
    # Other error
    except:
        print ("Some other error!")
    """def run_job():
        print("before_first_request is running connection successfull" )
        #time.sleep(0.0001)

    thread=threading.Thread(target=run_job)
    thread.start()"""

@app.route('/index')
def index():
    return "welcome to dronekit sitl service"

@app.route('/test')
def test():
    return "welcome to dronekit sitl 4444  service"


@app.route('/status_v2')
def get_state():
    global drone
    status=drone.vehicle.system_status.state
    return str(status)

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
    return drone.set_vehicle_mode(mode)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
