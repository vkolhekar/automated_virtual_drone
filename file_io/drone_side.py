from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException, Command
import dronekit_sitl
import time
import socket
import exceptions
import math
import argparse
from os import system
#declare const.
const = 180 / math.pi

#set desired altitude when take offs
desiredaltitude = 19

################Establish Connection with the quadcopter######
def connectCopter():
    system("QGC.AppImage 2>/dev/null&")
    ####Connecting to drone via mavlink#######################
    parser=argparse.ArgumentParser(description='commands')
    parser.add_argument('--connect')
    args=parser.parse_args()
    connection_string=args.connect
    try:
        vehicle=connect(connection_string,wait_ready=True)
        print("vehicle connected.")
    #Bad TCP connection
    except socket.error:
        print("No server exists.")
    #API error
    except APIException:
        print("Timeout.")
    #Bad TTY connection
    except exceptions.OSError as e:
        print("No serial exists.")
    #Other
    except:
        print("Unknown error.")

    return vehicle


def copterStatus():
    print("Inside copterStatus()")
    string="done "
    c.send( "*************Initial Vehicle Status *********************\n")
    c.send( "Get some vehicle attribute values:\n")
    c.send( " GPS: %s\n" % vehicle.gps_0)
    c.send( " %s \n" %vehicle.location.global_frame)
    c.send( " Battery: %s\n" % vehicle.battery)
    c.send( " Last Heartbeat: %s\n" % vehicle.last_heartbeat)
    c.send( " Is Armable?: %s\n" % vehicle.is_armable)
    c.send( " System status: %s\n" % vehicle.system_status.state)
    c.send( " Mode: %s\n" % vehicle.mode.name)    # settable
    c.send( " Changed Mode: %s\n" % vehicle.mode.name)
    c.send( " Roll in Euler Angle : %f \n" % float(vehicle.attitude.roll*const))
    c.send( " Pitch in Euler Angle : %f \n" % float(vehicle.attitude.pitch*const))
    c.send( " Yaw in Euler Angle : %f \n" % float(vehicle.attitude.yaw*const))
    c.send("done ")
    return string

######################MAIN()##################################
#Arm_and_takeoff(10)
vehicle=connectCopter()