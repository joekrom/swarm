#!/usr/bin/env python

import time
from pose import pose
from time import sleep

from pypozyx import (POZYX_POS_ALG_UWB_ONLY, POZYX_3D, Coordinates, POZYX_SUCCESS,
                        POZYX_ANCHOR_SEL_AUTO, DeviceCoordinates, PozyxSerial, get_first_pozyx_serial_port, SingleRegister, DeviceList,Quaternion,EulerAngles)



class ReadyToLocalize(object):
    """Continuously calls the Pozyx positioning function and prints its position."""

    def __init__(self, pozyx, anchors, algorithm=POZYX_POS_ALG_UWB_ONLY, dimension=POZYX_3D,remote_id=None):
        self.pozyx = pozyx

        self.anchors = anchors
        self.algorithm = algorithm
        self.dimension = dimension
        self.remote_id = remote_id

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        print("------------POZYX POSITIONING V1.1 -------------")
        print("NOTES: ")
        print("- No parameters required.")
        print()
        print("- System will auto start configuration")
        print()
        print("- System will auto start positioning")
        print()
        self.pozyx.printDeviceInfo(self.remote_id)
        print()
        print("------------POZYX POSITIONING V1.1 --------------")
        print()
        self.pozyx.clearDevices(self.remote_id)

        self.setAnchorsManual()
        self.printPublishConfigurationResult()

    def loop(self):
        """Performs positioning and displays/exports the data to the pixhawk
           verify if there is no error
           transform ENU coordinates to NED coordinates """
        position = Coordinates()
        status = self.pozyx.doPositioning(
            position, self.dimension, self.algorithm, remote_id=self.remote_id)
        if status == POZYX_SUCCESS:
            self.printPublishPosition(position)
            print"msg have been send to fc "
        else:
            self.printPublishErrorCode("positioning is not working")
            print"no msg was send"

    def printPublishPosition(self, position):
        """Prints the Pozyx's position and possibly sends it as a OSC packet"""
        network_id = self.remote_id
        if network_id is None:
            network_id = 0
        print("POS ID {}, x(mm): {pos.x} y(mm): {pos.y} z(mm): {pos.z}".format(
            "0x%0.4x" % network_id, pos=position))

        x = int(position.x)/1000
        y = int(position.y)/1000
        z = int(position.z)/1000
        q = quaternion()
        e = EulerAngles()
        self.pozyx.getQuaternion(q,self.remote_id)
        self.pozyx.getEulerAngles(e,self.remote_id)
        pose = pose(x,y,z,q,e)
        return pose


    def printPublishErrorCode(self, operation):
        """Prints the Pozyx's error and possibly sends it as a OSC packet"""
        error_code = SingleRegister()
        network_id = self.remote_id
        if network_id is None:
            self.pozyx.getErrorCode(error_code)
            print("LOCAL ERROR %s, %s" % (operation, self.pozyx.getErrorMessage(error_code)))

        status = self.pozyx.getErrorCode(error_code, self.remote_id)
        if status == POZYX_SUCCESS:
            print("xxxxx")
                 # (operation, "0x%0.4x" % network_id, self.pozyx.getErrorMessage(error_code)))

        else:
            self.pozyx.getErrorCode(error_code)
            print("ERROR %s, couldn't retrieve remote error code, LOCAL ERROR %s" %
                  (operation, self.pozyx.getErrorMessage(error_code)))
            # should only happen when not being able to communicate with a remote Pozyx.

    def setAnchorsManual(self):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        status = self.pozyx.clearDevices(self.remote_id)
        for anchor in self.anchors:
            status &= self.pozyx.addDevice(anchor, self.remote_id)
        if len(self.anchors) > 4:
            status &= self.pozyx.setSelectionOfAnchors(POZYX_ANCHOR_SEL_AUTO, len(self.anchors))
        return status

    def printPublishConfigurationResult(self):
        """Prints and potentially publishes the anchor configuration result in a human-readable way."""
        list_size = SingleRegister()

        self.pozyx.getDeviceListSize(list_size, self.remote_id)
        print("List size: {0}".format(list_size[0]))
        if list_size[0] != len(self.anchors):
            self.printPublishErrorCode("configuration")
            return
        device_list = DeviceList(list_size=list_size[0])
        self.pozyx.getDeviceIds(device_list, self.remote_id)
        print("Calibration result:")
        print("Anchors found: {0}".format(list_size[0]))
        print("Anchor IDs: ", device_list)

        for i in range(list_size[0]):
            anchor_coordinates = Coordinates()
            self.pozyx.getDeviceCoordinates(device_list[i], anchor_coordinates, self.remote_id)
            print("ANCHOR, 0x%0.4x, %s" % (device_list[i], str(anchor_coordinates)))
           # if self.osc_udp_client is not None:
               # self.osc_udp_client.send_message(
                   # "/anchor", [device_list[i], int(anchor_coordinates.x), int(anchor_coordinates.y), int(anchor_coordinates.z)])
                #sleep(0.025)

    def printPublishAnchorConfiguration(self):
        """Prints and potentially publishes the anchor configuration"""
        for anchor in self.anchors:
            print("ANCHOR,0x%0.4x,%s" % (anchor.network_id, str(anchor.coordinates)))
            #if self.osc_udp_client is not None:
               # self.osc_udp_client.send_message(
                   # "/anchor", [anchor.network_id, int(anchor.coordinates.x), int(anchor.coordinates.y), int(anchor.coordinates.z)])
               # sleep(0.025)
