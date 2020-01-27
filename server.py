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

##############Trial Function################################
def add(a,b):
    return(a+b)
    
###############Establish connection with PCM#################
def connectPCM():
    s = socket.socket()          
    print ("Socket successfully created") 
    # reserve a port on your computer in our 
    port = 12346          
    # Next bind to the port 
    # we have not typed any ip in the ip field 
    # instead we have inputted an empty string 
    # this makes the server listen to requests  
    # coming from other computers on the network 
    s.bind(('', port))         
    print ("socket binded to %s" %(port) )
    return s

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

#***************SENDING COMMANDS TO COPTER*******************#
###############Get current status of copter#################
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

#############Arm and Takeoff#################################
def copterArm_and_Takeoff(aTargetAltitude):
    #Arms vehicle and fly to aTargetAltitude.
    c.send ("Basic pre-arm checks \n")
    while not vehicle.is_armable:
        time.sleep(5)
    #this value was 1 at first, and there was too many "Waiting for vehicle to initialise..." messages.. so I modified.
    c.send ("Arming motors \n")
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True
    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        c.send( "Arming \n")
        time.sleep(1)
    c.send("****************************Taking off!*************************** \n")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    while True:
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            #c.send( "\nReached target altitude\n")
            
            break
        else:
            #.send("alt_wait")
            print( " Altitude: ", vehicle.location.global_relative_frame.alt)
            c.send ( " Altitude: %f \n " %vehicle.location.global_relative_frame.alt)
            time.sleep(1)
            #Break and return from function just below target altitude.
       
    #c.send("reached")
    c.send( "done ")
    return aTargetAltitude



###############################################################
def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


#########################################################################
def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint
###########READ UPLOADED MISSION FILE######################
def readmission(aFileName):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print("\nReading mission from file: %s" % aFileName)
    cmds = vehicle.commands
    missionlist=[]
    with open(aFileName) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])
                ln_autocontinue=int(linearray[11].strip())
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist




#############UPLOAD MISSION FILE#########################
def upload_mission(aFileName):
        """
        Upload a mission from a file.
        """
        #Read mission from file
        missionlist = readmission(aFileName)

        print ("\nUpload mission from a file: %s" % aFileName)
        #Clear existing mission from vehicle
        print ('Clear mission')
        cmds = vehicle.commands
        cmds.clear()
        #Add new mission to vehicle
        for command in missionlist:
            cmds.add(command)
        print ('Upload mission')
        vehicle.commands.upload()
        return "1"

##########UPLOAD MISSION FILE TO THE DRONE################
def upload_mission_file():
    mission_file="test_missions.txt"
    val=upload_mission(mission_file)
    if(val=="1"):
        c.send("Uploaded successfully \n ")
        c.send("done ")
    else:
        c.send("Could not upload file to the vehicle \n")
        c.send("done ")
################DOWNLOAD MISSION FILE#####################
def download_mission():
    missionlist=[]
    cmds=vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist
#################SAVE MISSION FILE############################
def save_mission():
    """
    Save a mission in the Waypoint file format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    aFileName='test_missions.txt'
    missionlist = download_mission()
    output='QGC WPL 110\n'
    for cmd in missionlist:
        commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
        output+=commandline
    with open(aFileName, 'w') as file_:
        file_.write(output)
    print("Mission saved")

#################START THE MISSION##################################
def start_mission():
    count=vehicle.commands.count
    print("count is %d" %count)
    print()
    print("Total number of waypoints is %s\n" %count)
    #vehicle.airspeed(11)
    vehicle.mode=VehicleMode("AUTO")
    new_waypoint=vehicle.commands.next
    current_waypoint=new_waypoint
    #while (count!=0):
    while (count-1!=new_waypoint):
        #print("Inside while loop")
       
        #vehicle.commands.next=count
        new_waypoint=vehicle.commands.next
        print("new waypoint is %s"%new_waypoint)
        if(current_waypoint==new_waypoint):
            if(new_waypoint=='0'):
                c.send("Distance to waypoint (%s) is 0 \n "%new_waypoint)
            else:
                c.send("Distance to waypoint (%s) is %s \n "%(new_waypoint, distance_to_current_waypoint()) )
            time.sleep(1)
        else:
            
            current_waypoint=new_waypoint   
            c.send("Distance to waypoint (%s) is %s \n "%(new_waypoint, distance_to_current_waypoint()) )
            time.sleep(1)
    '''dist=float(distance_to_current_waypoint())
    while(dist>0.6):
        c.send("Distance to waypoint (%s) is %s \n "%(new_waypoint, distance_to_current_waypoint()) )
        time.sleep(1)'''
    current_waypoint=new_waypoint
    ref=distance_to_current_waypoint()
    print("refrence is %s"%ref)
    while(distance_to_current_waypoint()>(float(ref)*.05)):
        c.send("Distance to waypoint (%s) is %s \n "%(new_waypoint, distance_to_current_waypoint()))
    print("Out of  loop")
    
    print("\n\n\n\t\t\tDone Surveying, returning home.")
    return_to_land()

###############RETURN TO LANDING ZONE##########################
def return_to_land():
    vehicle.mode=VehicleMode("RTL")
    while(vehicle.armed   == True):
        print("Waiting to be disarmed.")
    print("\n\nDISARMED")
    c.send("done ")
#******************************************************************#

###############SEND COMMANDS TO COPTER######################
def copterSHELL(cmd):
    if(cmd=='exit'):
        #print("inside exit if statement")
        c.close()
        exit()
    else:
        eval(cmd)



######################MAIN()##################################
#Arm_and_takeoff(10)
vehicle=connectCopter()
#save_mission()
s=connectPCM()
# put the socket into listening mode 
s.listen(5)      
print ("socket is listening" )
# Establish connection with client. 
c, addr = s.accept()      
print ('Got connection from', addr )
# send a thank you message to the client.  
c.send('Thank you for connecting') 
while True:
    cmd=c.recv(1024)
    #c.send(str(copterSHELL(cmd)))
    copterSHELL(cmd)
        