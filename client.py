######################IMPORT LIBRARIES#######################################
import socket                
import time
from os import system
#####################CONNECTING TO THE UAV####################################
def connectCopter():
    # Create a socket object 
    s = socket.socket()          
    
    # Define the port on which you want to connect 
    port = 12346   
    
    # connect to the server on local computer 
    s.connect(('127.0.0.1', port)) 
    # receive data from the server 
    print s.recv(1024)

    return s

#####################READING AND SEPERATING DATA###############################
############Utilities##########################################
def isspace(data):
	if((data==" ")or(data=="\n") ):
		return "space"
	else:
		return "alnum"

###########Get info from server#################################
def getACK():
    data=True
    done="done"
    rx_word=""
    new_line="\n"
    #rx_data_list=[]
    global new_data
    while data:
        new_data=""
        data=s.recv(1)
        #print(data)
        if(isspace(str(data))=="alnum"):
            rx_word+=str(data)
        else:
            #print("\nrx_word is "+rx_word)
            if(rx_word==done):
                #print rx_word
                #print("Detected done")
                break
            else:
                new_data+=rx_word+str(data)
                print new_data,
            rx_word=""

    return "0"

###############GETTING INITIAL STATUS##########################################
def getStatus():
    s.send('copterStatus()')
    val=getACK()
    return val


###############UPLOAD MISSION FILE#########################
def upload_mission():
    s.send('upload_mission_file()')
    val=getACK()
    return val

###############ARM AND TAKEOFF################################################
def Arm_and_takeoff():
    target_alt=input("Enter target altitude: ")
    s.send('copterArm_and_Takeoff(%s)' %target_alt)
    val=getACK()
    if(val=="Error"):
        print(val)
    else:
        print("\nReached Target altitude.")
    return "0"

#################START MISSION##################################
def start_mission():
    s.send('start_mission()')
    val=getACK()
    return "1"

####################MAIN##############################################################


################CALL REGULAR ROUTINES###################
def copter_routines():
    system('clear')
    print("\n**********Welcome to Routines**********\n")
    print("\nAvailable Routines are: \n1.R1\n\n")

    routine=raw_input("\nPlease select a Routine: ")
    if(routine=='R1'):
        print("\nCurrent status of the copter\n\n")
        val=getStatus()
        raw_input("Press Enter to continue...")
        print("\n\nUploading mission file\n\n")
        val=upload_mission()
        raw_input("Press Enter to continue...")
        print("\n\nArming vehicle\n\n")
        val=Arm_and_takeoff()
        system("clear")
        raw_input("\n\n\t\tCopter clear to takeoff\n\nPress Enter to begin\n")
        val=start_mission()
        print("\n\nRoutine completed")
        return "0"
    else:
        print("This Routine is not yet defined. Please try later.\n")
        return "0"
################MAIN()########################################################################
new_data=""
s=connectCopter()
print("\n***********Welcome to Copter Shell**************\n\n")
while(1):
    input_cmd=raw_input(">>")
    #print(input_cmd)
    if(input_cmd=='exit'):
        #print("inside if")
        s.send('exit')
        s.close()
        exit()
    else:
        ret_val=eval(str(input_cmd+"()"))
        if(ret_val=="Error"):
            print("Error occured")
        else:
            print("Operation Sucessful")
 
   
