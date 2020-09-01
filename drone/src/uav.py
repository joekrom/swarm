#!/usr/bin/env python
from dronekit import connect ,VehicleMode,LocationGlobalRelative
from pymavlink import mavutil
import time, threading

arm_mode = [
    'STABILIZE',
    'ALT_HOLD',
    'GUIDED_NOGPS'
]

modes_list=[
    'GUIDED',
    'LOITER',
    'RTL',
    'GUIDED',
    'POSHOLD',
    'AUTO',
    'LAND',
    'CIRCLE'
]

# Global position of the origin
lat = 51.806190 * 10**7 # lat wgs84 deg7
lon = 10.335161*10**7   #lon wgs84 deg7
alt = 585*1000 # real heiht in mm
time_usc = int (round(time.time()*1000000))

class Drone:


    def __init__(self):
        #self.vehicle = connect('udp:172.18.0.3:14552',baud=115200,wait_ready=True,heartbeat_timeout=180)
        self.vehicle = connect('tcp:192.168.0.14:5763',baud=115200,wait_ready=True,heartbeat_timeout=180)
        self.pose = {}

    # def set_vehicle_mode(self,mode):
    #     self.vehicle.mode=VehicleMode(mode)
    #     time.sleep(1)
    #     return "vehicle mode changed with success"

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

    def set_vehicle_mode(self,mode):
        self.vehicle.mode = VehicleMode(mode)

    def get_vehicle_mode(self):
        return self.vehicle.mode.name

    def get_pose(self):
        self.pose['north'] = self.vehicle.location.local_frame.north # x cooedinate in ned
        self.pose['east'] = self.vehicle.location.local_frame.east   # y cooedinate in ned
        self.pose['down'] = self.vehicle.location.local_frame.down  # z cooedinate in ned
        return self.pose

    def get_bsi(self):
        return self.vehicle.battery.level


    # function to arm  the vehicle
    def arm_vehicle(self):
        armed = False
        print (" we check if the vehicle is on armable mode ")
        mode = self.get_vehicle_mode()
        _mode = str(mode)
        if  mode in arm_mode:
            print ("Arming motors")
            self.vehicle.armed = True
            while not self.vehicle.armed:
                time.sleep(1)
            armed = True
        return armed



    #command to send to the vehicle
    def arm_disarm_vehicle(self,value):
        if not self.vehicle.armed and value :
            if not self.vehicle.is_armable:
                print("waiting for vehicle to be armable")
                print("arming motors")
                self.vehicle.armed=True
            while not self.vehicle.armed:
                print("wait for arming to take effect ")
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
        # check if the vehicle is in a mode that can be armed
        mode = get_vehicle_mode()
        #if mode in arm_mode:
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
        #self.vehicle.close()

    def set_gps_origin(self):
        msg_1 = self.vehicle.message_factory.set_gps_global_origin_encode(
        0, # target_system --> 0 broadcast to everyone
        int(lat),int(lon),int(alt) # latitude,longitude,altitude
        #time_usc
        )
        self.vehicle.send_mavlink(msg_1)

    def set_home_position(self):
        msg_2 = self.vehicle.message_factory.set_home_position_encode(
        0, # target_system
        int(lat),int(lon),int(alt),

        x = 0, #Local X position of this position in the local coordinate frame
        y = 0, #Local Y position of this position in the local coordinate frame
        z = 0, #Local Z position of this position in the local coordinate frame
        q = [1,0,0,0], # w,x,y,z Used to indicate the heading and slope of the ground

        approach_x = 0,
        approach_y = 0,
        approach_z = 1
        )
        self.vehicle.send_mavlink(msg_2)

    def init_gps_lock(self):
        #for i in range (0,2):
        self.set_gps_origin()
        self.set_home_position()
        time.sleep(0.2)
        print("gps_oringin and home_position initialized")

    def pozyx_to_fc(self, x,y,z,q):
        pozyx_data_msg = self.vehicle.message_factory.att_pos_mocap_encode(
            time_usc,
            q = q,#[1,0,0,0],
            x = x, # X position (NED )
            y = y, # Y position (NED )
            z = -z # Z position (NED )
        )
        self.vehicle.send_mavlink(pozyx_data_msg)
        print("mocap published to fc ")




    def pull_out(self,alt):
        #get the vehicle mode
        # msg = self.vehicle.message_factory.set_position_target_local_ned(
        #     0, # timeboot in ms
        #     0,0, # target system and target_component
        #     mavutil.mavlink.MAV_FRAME_BODY_NED,#Frame
        #     0,0,alt,# north,east,down
        #     0,0,0,# vx.vy,vz
        #     0,0 # yaw and yaw_rate
        # )

        mode = self.get_vehicle_mode()
        _mode = str(mode)
        if _mode not in arm_mode:
            # switch mode
            self.set_vehicle_mode(arm_mode[0]) #stabilize mode
        # while not self.get_vehicle_mode() in arm_mode:
        #     time.sleep(1)
        print("vehicle is armable ")
        # now we can arm the drone
        self.vehicle.armed = True
        while not self.vehicle.armed:
            time.sleep(1)
        print("vehicle is armed")

        """ use set_attitude target or
            position_target_local_ned """

        print("takeoff")
        # switch to the GUIDED mode
        self.set_vehicle_mode(modes_list[0])
        time.sleep(2.0)
        # #self.vehicle.go_to_position_target_local_ned(0,0,alt)
        self.vehicle.simple_takeoff(alt)
        # wait until the vehicle reaches a safe height before processing the goto
        while True:
            # get the local altitude
            current_altitude = self.vehicle.location.local_frame.north
            if current_altitude >= alt*0.95:
                print("reached target altitude ")
                # now we can land
                break
            time.sleep(1)

        # hover for 10 seconds
        time.sleep(10)
        print("now let us land ")
        self.vehicle.mode("LAND")
        # return to stabilize mode
