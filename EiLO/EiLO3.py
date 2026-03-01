# Externally Integrated Lights Out (EiLO) Verion 3.0
# Build 190, Febuary 20th 2026
# Copyright (c) 2025 - 2026, Backdoor Interactive, Phoenix

# This is the main EiLO 3 Program. Its ment to be ran on a small linux computer. (Preferably a raspberry pi)
# Future ideas: Make an effort to allow for windows serial communcation to the controller instead
# Recomended python version: 3.8.8

# If you ever want to try this software out, Or if you need help setting it up. Ask me, id love to help

import serial, os, requests, sys, time, socket, threading, datetime, platform, subprocess
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from getpass import getpass
# For Windows # from pythonping import ping 

name = os.name
def clearscreen():
    global name
    if name == "nt":
        os.system("cls")
    else:
        os.system("clear")
clearscreen()

debug = 0
def logprint(message,option=""):
    global debug
    if debug == 1:
        if option != "":
            print(message,option)
        else:
            print(message)
    else:
        ae = 1 # print("ae")






# For the webserver: The default account username is: Administrator, The password is EiLO3's master password (or the password to login to the terminal locally)"
# (You set this password during the inital setup when you run this script for the first time!)


automatedaction = ""
powerstate = 0 # System Power State 0 - off 1 - on 2 - Process of booting up
hostpower = 0 # Host power state
phnyautostartenabled = 0

# IP Address cashe list
# When ever a user logs in. there IP address gets stored here. They have 1 hour before its removed from this list and they have to login again.
authenticatedAddresses = [] # Users have a 1 hour session
authusers = [] # another list to map ips to usernames
# If you want. you can add an ip address Example:
# authenticatedAddresses = ["192.168.0.148","127.0.0.1","98.43.65.127"]
# (replace them with your own)
# to permanitely allow that ip in. they can be local or internet ip's
permissions = ["1,1,1,1,1,1"] # This gets updated as more users get created. Default unchangeable permissions for the administrator account

class configuration:
    def accountrebuild():
        # this gets iloconfig.txt accounts in proper order
        mainstring = "WEBACCESS\n"
        global users
        global paswds # todo. make hashing
        global permissions
        for i in range(len(users)):
            if i != 0:
                # add the users, one at a time. there are 3 lines
                # username
                # password
                # permissionstring
                mainstring = mainstring + f"{users[i]}\n{paswds[i]}\n{permissions[i]}\n"

            else:
                # skip over default admin acc
                ae = 1 # very funny variable!!!
        # now all accounts are in the string,
        # close it off
        mainstring = mainstring + "ENDWEB\n"
        logprint(mainstring)
        return mainstring

    def readiloconfig(newline=0): # config reader
        configarray = []
        fn = "iloconfig.txt"
        with open(fn) as f:
            for line in f:
                if newline == 0:
                    new = line.split("\n")
                    configarray.append(new[0])
                else:
                    configarray.append(line)
        EventLog.eventwrite("Read configuration successfully")
        return configarray # outputs array xd
    
    def updateaccounts():
        logprint("Account update! (commit to iloconfig)")
        with open("iloconfig.txt", "r+") as f:
            d = f.readlines()
            logprint(d)
            foundit = 0
            for i in range(len(d)):
                logprint(d[i])
                if d[i] == "WEBACCESS\n":
                    foundit = 1
                    logprint(f"new file output: \n{d[:i]}")
                    f.seek(0)
                    f.write("") # Erase the file
                    f.writelines(d[:i]) # Restore the file
                    logprint(configuration.accountrebuild())
                    f.write(f"{configuration.accountrebuild()}") # Rebuild the newest account hiarchy
            # success?
            if foundit == 1:
                logprint("Success in updating users!")
                # clean up the end of the file
            else:
                # append WEBACCESS to the bottom of the config and rerun
                f.write("WEBACCESS\n")
                f.close()
                configuration.updateaccounts()
            
            f.close() # delete user account db


class EventLog:
    def geteventlog(br=0):
        mainstring = ""
        mainarray = []
        fn = "eventloggy.txt"
        try:
            with open(fn,"r") as ae:
                for line in ae:
                    #logprint(line)
                    if br == 0:
                        mainstring = mainstring + line.rstrip("\n")
                        #logprint(mainstring)
                        mainarray.append(line.rstrip("\n"))
                    else:
                        mainstring = mainstring + line.replace("\n","<br>")
                        #logprint(mainstring)
                        mainarray.append(line.replace("\n","<br>"))
            ae.close()
            return mainarray,mainstring
        except:
            return ["[Event log empty]"],"[Event log empty]"
    def cleareventlog():
        fn = "eventloggy.txt"
        with open(fn,'w') as ae:
            ae.writelines([""])
            ae.close()
    def eventwrite(log):
        fn = "eventloggy.txt"
        try:
            with open(fn,'r+') as ae:
                content = ae.read()
                now = datetime.datetime.now()
                thestring = f"[{now}] {log}\n"
                ae.seek(0,0)
                ae.write(thestring.rstrip('\r\n') + '\n' + content)
                ae.close()
        except:
            with open(fn,'w') as ae:
                now = datetime.datetime.now()
                thestring = f"[{now}] {log}\n"
                ae.write(thestring)
                logprint("Even log cleared!")
                ae.close()
EventLog.eventwrite("----------------")
EventLog.eventwrite("EiLO3 Started up!")


def getpowerstate():
    global powerstate
    if powerstate == 1:
        return "ON"
    if powerstate == 0:
        return "OFF"
    if powerstate == 2:
        return "Startup in progress / Network Unreachable"
    if powerstate == 3:
        return "Shutdown in progress / Network Unreachable"


# Setup / Initial Configuration
if os.path.isfile("iloconfig.txt") != True:
    print("--------------\nWelcome to EiLO 3!\n--------------\n\nInital configuration for Lights Out Management\n")
    print("-- Some terminology --\nHost: The computer in which EiLO3 controls\nServer: The device in which EiLO3 is running on (This device!)\n")
    print("Please enter the following information about the current setup:")
    print("")
    cname = input("A small name for the computer which EiLO is installed in:\n> ")
    longcname = input("The full Manafactuer/model of the computer which iLO is installed in:\n> ")
    host = input("The computers network hostname: \n> ")
    print("Now create a password for the Administrator account\nNote the input is hidden for security")
    adminpass = getpass("password \n> ")
    print("Password accepted!")
    clearscreen()
    print("Password accepted")
    print("Enter the port number for remote terminal/console sessions (Default is 5000)")
    while True:
        try:
            port = int(input("> "))
            print("Port accepted!")
            time.sleep(0.5)
        except:
            print("Invalid! Please make sure your answer is an integer")
        break
    print("OPTIONAL: Enter in a Discord bot token to host a remote management bot to control this EiLO 3 from.")
    print("To skip this: Simply press [ENTER]")
    token = str(getpass("> "))
    if token == "":
        token = "NONE"
    clearscreen()
    print("OPTIONAL: Enter in a discord webhook to send Logs and other information to")
    print("To skip this: Simply press [ENTER]")
    weburl = str(getpass("> "))
    if weburl == "":
        weburl = "NONE"
    clearscreen()

    print("Enter the static IP Address of the system EiLO 3 is connected to. (This is to determine power status)")
    ipaddress = str(input("> "))
    print("Enter a port to host the webserver on (Recomended default is 8080)")
    webport = str(input("> "))
    print("Enter a port to use with virtual media (Recomended default is 8800)")
    virport = str(input("> "))
    print("Enter a port to use (locally) with the EiLO Client Application media (Recomended default is 5100)")
    cliport = str(input("> "))
    print("Enter a baud rate which the serial connection to the controller uses (default is 9600)")
    baud = str(input("> "))
    clearscreen()
    motd = "This is a private system. It is to be used solely by authorized users and may be monitored for all lawful purposes. By accessing this system, you are consenting to such monitoring."
    print("Great, all set!")
    print("Saving settings to iloconfig.txt - Please wait...")
    data = [f"{cname}\n",f"{longcname}\n",f"{host}\n",f"{adminpass}\n",f"{port}\n",f"{token}\n",f"{ipaddress}\n",f"{weburl}\n",f"{webport}\n",f"{motd}\n",f"{virport}\n",f"{cliport}\n",f"{baud}\n"]
    with open("iloconfig.txt", 'w') as file:
        file.writelines(data)
        file.close()
    time.sleep(0.2)
    print("EiLO3 Configuration Saved Successfully. EiLO3 Must reset to apply changes\n\n-- Please restart EiLO3 --")
    input("\n[PRESS ANY KEY TO EXIT EILO3]\n")
    exit()
else:
    config = configuration.readiloconfig()
    print("Externally Integrated Lights-Out Version 3.0 (Build 1.90, Feb 20th 2026)\nLoading configuration...")
    time.sleep(0.7)
    password = config[3] # Password to access controls
    computername = config[0] # A custom name that you like to call the remote system
    longcomputername = config[1] # Full remote computer name
    mgmthostname = config[2] # The computer name of the system lights out is connected too
    terminalport = int(config[4])
    localip = str(config[6])
    dct = str(config[5])
    weburl = str(config[7])
    httpport = int(config[8])
    motd = str(config[9])
    virport = int(config[10])
    cliport = int(config[11])
    baudrate = int(config[12])
    # Webserver login information
    # These are constants and cannot be changed during operation. Only accounts that get appened below are changeable
    users = ["Administrator"]
    paswds = [f"{password}"]

    # webserver userpass loop
    for i in range(len(config)):
        thestring = "WEBACCESS"
        if config[i] == thestring:
            scanfin = 0
            startindex = i
            aeindex = 1 # start @ 1
            # Found user pass section
            while True:
                try:
                    if config[startindex+aeindex] != "ENDWEB":
                        # this an entry
                        logprint("Found webserver user/pass")
                        logprint("Username: ",config[startindex+aeindex])
                        logprint("Password: ",config[startindex+aeindex+1])
                        logprint("\n[Appended to the list of allowed users for webserver]")
                        mainuser = config[startindex+aeindex]
                        mainuser = mainuser.split("\n")
                        mainuser = mainuser[0]
                        mainpass = config[startindex+aeindex+1]
                        mainpass = mainpass.split("\n")
                        mainpass = mainpass[0]
                        mainperm = config[startindex+aeindex+2]
                        mainperm = mainperm.split("\n")
                        mainperm = mainperm[0]
                        users.append(mainuser)
                        paswds.append(mainpass)
                        permissions.append(mainperm)
                        # now do ae
                        aeindex = aeindex + 3
                    else:
                        # thats the end!
                        scanfin = 1
                        break
                except:
                    logprint("thats the end of the web creds")
                    break
            logprint("Finished webserver user/pass scan")
    




def printlog(message):
    EventLog.eventwrite(message)
    global weburl
    data = {
        "username": "EiLO 3 Logs", 
        "content": "*New log message*", 
        "embeds": [{ 
        "title": "Externally-Integrated Lights-Out 3.0 *(build 190)*",
        "description": message 
        }]
    }
    if weburl != "NONE":
        x = requests.post(weburl, json=data) # send the message


def updatetime(hour,pm):
    with open("config.txt", "w") as f:
        hourmil = hour
        if pm == 1:
            hourmil = hourmil + 12
        logprint(f"Military time: {hourmil}")
        f.write(f"{hourmil}")

if os.path.isfile("config.txt") != True:
    print("ADDONS: Phnyautostart doesnt have a config file! Ill create one now. (config.txt)")
    updatetime(6,0)
    print("")
    print("NOTE: The system has defaulted autostart to OFF! To configure this, see the autostart command")
    print("Default autostart hour: 6 A.M.")



def customaction():
    global powerstate
    printlog(f"{computername} | CONSOLE | AUTOMATED TIME EVENT: PhnyAutoStart Triggered!")
    writeserialdata(b"A")
    powerstate == 1
    time.sleep(3800) # Wait around a little more than an hour to prevent retriggering.

def readconfig():
    fn = "config.txt"
    with open(fn) as f:
        for line in f:
            hourmain = int(line.rstrip()) 
            f.close()
            return hourmain

def chck(confh):
    while True:
        time.sleep(60)
        global phnyautostartenabled
        if phnyautostartenabled == 0:
            return
        dtime = datetime.datetime.now()
        hour = dtime.hour
        if hour == confh:
            while True:
                print("PhnyAutoStart Its time to turn on!")
                customaction()
                break
                
def phnyautostart():
    while True:
        global phnyautostartenabled
        if phnyautostartenabled == 0:
            ae = 1
        else: 
            print("Init PhnyAutoStart!\nPhnyAutoStart Preparing... ~30 seconds till first operation.")
            time.sleep(30)
            print("PhnyAutoStart Ready!")
            chck(readconfig())
        time.sleep(5)


def writeserialdata(msg):
    global baudrate
    connected = 0
    # For linux first
    try:
        logprint("INIT EiLO Serial To Arduino")
        time.sleep(0.5)
        logprint("Attempting to connect on ACM0")
        ser = serial.Serial('/dev/ttyACM0',baudrate, timeout=1)
        logprint("Connection to the system Successful!")
        connected = 1
    except:
        logprint("Failed on ACM0")
        try:
            logprint("Attempting to connect on ACM1")
            ser = serial.Serial('/dev/ttyACM1',baudrate, timeout=1)
            logprint("Connection to the system Successful!")
            connected = 1
        except:
            logprint("Failed on ACM1")
            try:
                logprint("Attempting to connect on ACM2")
                ser = serial.Serial('/dev/ttyACM2',baudrate, timeout=1)
                logprint("Connection to the system Successful!")
                connected = 1
            except:
                logprint("Failed ACM2")
                try:
                    logprint("Attempting to connect on ACM3")
                    ser = serial.Serial('/dev/ttyACM3',baudrate, timeout=1)
                    logprint("Connection to the system Successful!")
                    connected = 1
                except:
                    logprint("Could not connect to the controller (Is the interface connected?)\nContinuing anyway...")
                    connected = 0
                    time.sleep(1)
    if connected == 1:
        ser.flush()
        logprint("intentional delay, 4 seconds")
        time.sleep(4)
        logprint(f"Sending message: {msg}")
        ser.write(msg)
        EventLog.eventwrite(f"Sent '{msg}' over serial to controller")


    # This is the CLI for the remote console
def parsecommand(username, cmd):
    global computername
    global powerstate
    global motd
    global authusers
    global users
    global paswds
    global permissions
    if cmd == "help":
        #print("ae")
        return f"<{username}>@{computername}_EiLO $ ","EiLO 3 Remote Console CLI Help\n\npower <type>      Performs an action on the Power Button\n  |---power momentary   Press the Power button once\n  |---power hold        Press and hold the Power button for 5 seconds\n  |---power coldboot    Power hold followed by a momentary.\n  |---power reset       Reset the system\n\nGeneral Configuration\nUsers\n\nshow users   Show existing user accounts followed by there permission string\nshow users http   show users currently logged into an active session via HTTP\ncreate user <username> <password> <permstring>   Create a user account\nedit user <username> <newpass> <newperm>   Modify an existing user\ndelete user <username>   Delete an existing user\n\n\nconfig motd <message>   Customize the login security banner\n\noem_eiloping <ipaddress>   Ping an IP address through EiLO\noem_clientping <ipaddress>   Ping an IP Address through the client\n\n\nEnd of help! (for now ;)"
    if cmd == "power on":
        writeserialdata(b"A")
        printlog(f"{computername} | The Virtual Power Button was pressed momentarily remotely")
        return f"<{username}>@{computername}_EiLO $ ", "Server powering on..."
    if cmd == "power momentary":
        writeserialdata(b"A")
        printlog(f"{computername} | The Virtual Power Button was pressed momentarily remotely")
        return f"<{username}>@{computername}_EiLO $ ", "Server Power Pressed Momentarily"
    if cmd == "power hold":
        writeserialdata(b"B")
        printlog(f"{computername} | The Virtual Power Button was pressed and held remotely")
        return f"<{username}>@{computername}_EiLO $ ", "Server Power Button Pressed and Held (Released after 5 seconds)"
    if cmd == "power coldboot":
        writeserialdata(b"B")
        time.sleep(10)
        writeserialdata(b"A")
        printlog(f"{computername} | Cold boot initated remotely")
        return f"<{username}>@{computername}_EiLO $ ", "System cold rebooted"
    if cmd == "power reset":
        writeserialdata(b"C")
        printlog(f"{computername} | Reset initated remotely")
        return f"<{username}>@{computername}_EiLO $ ", "Server reset"
    if cmd == "config":
        doconfig(0)
        return f"<{username}>@{computername}_EiLO $ ", "ae"
    if cmd == "show users http":
        thestring = "Currently active user sessions on HTTP:\n"
        for i in range(len(authusers)):
            thestring = thestring + f"{authusers[i]}\n"
            logprint(thestring)
        return f"<{username}>@{computername}_EiLO $ ", thestring
    if cmd == "show users":
        thestring = "Current users registered into EiLO:\n"
        for i in range(len(users)):
            thestring = thestring + f"Username: {users[i]} - Permissions: {permissions[i]}\n"
            logprint(thestring)
        return f"<{username}>@{computername}_EiLO $ ", thestring
    # now for config commands
    if cmd.startswith("create user"):
        http,irc,virt,pwer,sett,admin = EiLO.getpermsuser(username,1)
        logprint("admin:",admin)
        if admin == 1 or admin == "1" or admin == " 1" or admin == "1 " or admin == " 1 ":
            try:
                ae = cmd.split("create user")
                ae = ae[1]
                ae = ae.split(" ")
                logprint(ae[1]) # un
                logprint(ae[2]) # pw
                logprint(ae[3]) # pm
                unamemain = ae[1]
                pswmain = ae[2]
                permstring = ae[3]
                # create the user
                cancontinue = 1
                for i in range(len(users)):
                    if users[i] == unamemain:
                        return f"<{username}>@{computername}_EiLO $ ", f"ERROR: The account: {unamemain} already exists"
                        cancontinue = 0
                if cancontinue == 1:
                    users.append(unamemain)
                    paswds.append(pswmain)
                    permissions.append(permstring)
                    logprint("\n\naccounts updated:\n\n")
                    logprint(users)
                    logprint(paswds)
                    time.sleep(2)
                    configuration.updateaccounts()
                    return f"<{username}>@{computername}_EiLO $ ", f"Successfully created a new user under the username of {ae[1]}\nNote: It may take up to 30 seconds for the changes to apply globally"
            except:
                return f"<{username}>@{computername}_EiLO $ ", "create user <username> <password> <permission-string>\nExample of a permission string: 1,1,1,0,0,0\nAccess to HTTP, Access to Remote Console, Access to Virtual Media, Access to Power button controls, Can change EiLO Settings, Can Administrate Users"
        else:
            return f"<{username}>@{computername}_EiLO $ ", f"ERROR: Insuffciant Permissions\nYour account {username} does not have the required permissions to administor EiLO user accounts to the server"

    if cmd.startswith("delete user ") == 1:
        http,irc,virt,pwer,sett,admin = EiLO.getpermsuser(username,1)
        logprint("admin:",admin)
        if admin == 1 or admin == "1" or admin == " 1" or admin == "1 " or admin == " 1 ":
            ae = cmd.split("delete user ")
            ae = ae[1]
            logprint(f"request over remote console to delete user: {ae}")
            ae = ae.replace(" ","")
            if ae == "Administrator":
                return f"<{username}>@{computername}_EiLO $ ", f"ERROR: Cant delete the Administrator account"
            EiLO.deleteuser(ae)
            return f"<{username}>@{computername}_EiLO $ ", f"Successfully deleted user: {ae}"
        else:
            return f"<{username}>@{computername}_EiLO $ ", f"ERROR: Insuffciant Permissions\nYour account {username} does not have the required permissions to administor EiLO user accounts to the server"

    if cmd.startswith("edit user ") == 1:
        http,irc,virt,pwer,sett,admin = EiLO.getpermsuser(username,1)
        logprint("admin:",admin)
        if admin == 1 or admin == "1" or admin == " 1" or admin == "1 " or admin == " 1 ":
            ae = cmd.split("edit user ")
            ae = ae[1]
            ae = ae.split(" ")
            uname = ae[0]
            pwd = ae[1]
            perm = ae[2]
            if uname in users:
                logprint("ok we good!")
            else:
                return f"<{username}>@{computername}_EiLO $ ", f"ERROR: User: {uname} does not exist, Use show users to check a list of available users!"
            logprint(f"request over remote console to edit user: {uname}")
            
            
            if ae == "Administrator":
                return f"<{username}>@{computername}_EiLO $ ", f"ERROR: Cant edit the Administrator Account"
            EiLO.deleteuser(ae[0])
            time.sleep(0.5)
            # now re add
            users.append(uname)
            paswds.append(pwd)
            permissions.append(perm)
            logprint("\n\naccounts updated:\n\n")
            logprint(users)
            logprint(paswds)
            time.sleep(1)
            configuration.updateaccounts()
            return f"<{username}>@{computername}_EiLO $ ", f"Successfully edited user: {uname}"
        else:
            return f"<{username}>@{computername}_EiLO $ ", f"ERROR: Insuffciant Permissions\nYour account {username} does not have the required permissions to administor EiLO user accounts to the server"

    if cmd.startswith("config motd") == 1:
        ae = cmd.split("config motd")
        newmotd = f"{ae[1]}\n"
        newmotd = newmotd.replace(r"\n","\n")
        if newmotd.startswith(" ") == 1:
            newmotd = newmotd[1:]
        settings = configuration.readiloconfig(1)
        index = 9
        with open("iloconfig.txt", 'w') as file:
            settings[index] = newmotd
            logprint("new config:",settings)
            logprint("\nnew MOTD:",settings[index]) 
            global motd
            motd = newmotd
            file.writelines(settings)
            file.close()
            return f"<{username}>@{computername}_EiLO $ ", f"Successfully changed MOTD"
           
    if cmd == "exit":
        return f"<{username}>@{computername}_EiLO $ ", f"Ending Remote Console Connection&&exit"
    else:
        return f"<{username}>@{computername}_EiLO $ ", "\nstatus=0\nCommand Processing Failed.\n"    

# some help displays

def help(cmd=""):
    print("The WebUI is used to configure most options")
    if cmd == "power":
        print("power <type>      Performs an action on the Power Button")
        print("  |---power momentary   Press the Power button once")
        print("  |---power hold        Press and hold the Power button for 5 seconds (Will force shutdown)")
        print("  |---power coldboot    Power hold followed by momentary. Resulting in a cold boot")
        print("  |---power reset       Reset the system")
        print("  Short commands\n  |---power on       Turn on the system")
        print("  |---power off       Logically power off the system")
    else:
        print("iLO help\npower <type>      Performs an action on the Power Button\n  |---power momentary   Press the Power button once\n  |---power hold        Press and hold the Power button for 5 seconds (Will force shutdown)\n  |---power coldboot    Power hold followed by momentary. Resulting in a cold boot\n  |---power reset       Reset the system\nMore commands coming soon.")
        print("")
        print("config <option>    Configure certain settings in EiLO3")
        print("  |----motd        Change the message of the day login banner")
        print("")
        print("")
        print("\nShort commands for power\n  |---power on       Turn on the system")
        print("  |---power off       Logically power off the system")

        print("More commands over on IRC!")
        print("End Help")
    command()

def help(cmd=""):
    if cmd == "power":
        print("power <type>      Performs an action on the Power Button")
        print("  |---power momentary   Press the Power button once")
        print("  |---power hold        Press and hold the Power button for 5 seconds (Will force shutdown)")
        print("  |---power coldboot    Power hold followed by momentary. Resulting in a cold boot")
        print("  |---power reset       Reset the system")
        print("  Short commands for power\n  |---power on       Turn on the system")
        print("  |---power off       Logically power off the system\n")
        command()

    else:
        print("EiLO 3 help\n")
        print("power <type>      Performs an action on the Power Button")
        print("  |---power momentary   Press the Power button once")
        print("  |---power hold        Press and hold the Power button for 5 seconds (Will force shutdown)")
        print("  |---power coldboot    Power hold followed by momentary. Resulting in a cold boot")
        print("  |---power reset       Reset the system")
        print("\nShort commands\n  |---power on        Turn on the system")
        print("  |---power off       Logically power off the system\n")
        print("autostart      Configure PhnyAutoStart")
        print("More commands on IRC!")
        print("End Help")
    command()


def doconfig():
    # Configurationp
    print("wip")



def command(): # This is locally
    global powerstate
    global debug
    cmd = str(input(f"{computername} EiLO > "))
    if cmd == "help":
        print("")
        print("")
        help()
    if cmd == "log":
        debug = 1
        print("Logging to console Enabled")
        command()
    if cmd == "no log":
        debug = 0
        print("Logging to console Disabled")
        command()
    if cmd == "config":
        doconfig(0)
    if cmd == "ae":
        clearscreen()
        print("ae")
        # special ae prompt
        ae = input("ae!>")
        if ae == "ae":
            print("ae")

        command()
    if cmd == "autostart":
        print("\nPhnyAutoStart - Version 1.0\n")
        print("Program Help")
        print("autostart time=<am/pm> hour=<hour>  --  Set the time to which PhnyAutoStart Operates at")
        print("autostart on -- Enable PhnyAutoStart")
        print("autostart off -- Disable PhnyAutoStart\n")
        command()
    if cmd == "autostart on":
        # enable
        print("PhnyAutoStart Enabled")
        global phnyautostartenabled
        phnyautostartenabled = 1
        command()
    if cmd == "autostart off":
        print("PhnyAutoStart Disabled")
        phnyautostartenabled = 0
        command()
    try:
        thesplit = cmd.split("hour=")
        if str(thesplit[0]) == "autostart time=am ":
            print(f"PhnyAutoStart will boot the system at {thesplit[1]} A.M. Every day")
            updatetime(int(thesplit[1]),0)
            command()
        if str(thesplit[0]) == "autostart time=pm ":
            print(f"PhnyAutoStart will boot the system at {thesplit[1]} P.M. Every day")
            updatetime(int(thesplit[1]),1)
            command()
    except:
        ae = 1
    if cmd == "power":
        global powerstate
        global localip
        print("Determining Host Status...")
        print(f"{getpowerstate()}")
        pingresult = SysInfo.pinghost(6) # try to contact the host 6 times
        if pingresult == 1:
            print("EiLO 3 detected that the Host System is ON. It can be pinged!")
        else:
            powerstate = 0
            print("EiLO 3 detected that the Host System is OFF. Cant ping it!")
            ans = input("Is this correct? (y/n)> ")
            if ans == "y":
                powerstate == 0
            if ans == "n":
                print(f"\nERROR: Unable to determine power status of the Host! Cant ping {localip}\n")

    if cmd == "power on":
        powerstate = 2
        print("Host System Powering ON...")
        writeserialdata(b"A")
        printlog(f"{computername} | The Virtual Power Button was pressed momentarily remotely")
        command()
    if cmd == "power off":
        powerstate = 3
        writeserialdata(b"A")
        writeserialdata(b"A") # I press it a second time just in case pressing it once turned on the screen
        print("Host System Safely Powering OFF")
        printlog(f"{computername} | The Virtual Power Button was pressed momentarily remotely")
        command()
    if cmd == "power momentary":
        print("Pressing Power button Momentarily")
        writeserialdata(b"A")
        printlog(f"{computername} | The Virtual Power Button was pressed momentarily remotely")
        command()
    if cmd == "power hold":
        print("Holding the Power Button for 5 seconds")
        powerstate = 3
        writeserialdata(b"B")
        printlog(f"{computername} | The Virtual Power Button was pressed and held remotely")
        command()

    if cmd == "power coldboot":
        print("Cold boot initiated!\nForce shutdown...")
        writeserialdata(b"B")
        time.sleep(10)
        print("Restoring power...")
        writeserialdata(b"A")
        print("Coldboot executed successfully\nThe system is turning on again")
        printlog(f"{computername} | Cold boot initated remotely")
        powerstate = 2
    if cmd == "power reset":
        print("Resetting the system")
        writeserialdata(b"C")
        command()
        powerstate == 2
    if cmd == "exit":
        print(f"Logging out of {computername} EiLO")
        exit()
    if cmd == "config motd":
        print("Enter a new Message of the Day banner (MOTD) to display on the login screen")
        msg = input("> ")
        settings = configuration.readiloconfig()
        index = len(settings) - 1
        print(f"Will overwrite the following message: {settings[index]}\nIs this Ok?")
        ae = input("(y/n) > ")
        if ae == "n" or ae == "":
            print("Canceled.")
            time.sleep(1)
            print("The operation was canceled by the user. Returned to CLI")
        else:
            with open("iloconfig.txt", 'w') as file:
                settings[index] = msg
                print(settings[index])
                file.writelines(settings)
                file.close()
            print("Configuration updated successfully, Changes will take effect immdiately")
            motd = msg
            print( "The command completed succesfully")
            return 0
    else:
        print("\nstatus=0\nCommand Processing Failed.\n")    
        command()

def automatedserial(input):
    print("Automated Serial Command!")
    enc = f'{input}'.encode()
    writeserialdata(enc)
    print("Complete!")
    sys.exit()



# host_key = paramiko.RSAKey.generate(2048)
# 
# class Server(paramiko.ServerInterface):
#     def check_auth_password(self, username, password):
#         if (username == 'testuser') and (password == 'testpassword'):
#             return paramiko.AUTH_SUCCESSFUL
#         return paramiko.AUTH_FAILED
# 
#     def get_allowed_auths(self, username):
#         return 'password'
# 
# def handle_connection(client_socket):
#     try:
#         transport = paramiko.Transport(client_socket)
#         transport.add_server_key(host_key)
#         server = Server()
#         try:
#             transport.start_server(server=server)
#         except paramiko.SSHException:
#             print('SSH negot failed.')
#             return
#         channel = transport.accept(20)
#         if channel is None:
#             print('no channel')
#             return
# 
#         print('ssh authentication success')
#         channel.send('EiLO3 SSH v0.1\n')
#         channel.send('Commands: test, quit\n')
#         while True:
#             command = channel.recv(1024).decode('utf-8').strip()
#             if not command:
#                 continue
#                 
#             if command == 'quit':
#                 channel.send('Goodbye!\n')
#                 break
#             elif command == 'test':
#                 channel.send(f'test command\n')
#             else:
#                 channel.send(f"Unknown command: {command}\n")
# 
#         channel.close()
#         transport.close()
# 
#     except Exception as e:
#         print(f'ssh ae1: {e}')
#         try:
#             transport.close()
#         except:
#             pass
# 
# def sshservy():
#     global sshport
#     port = sshport
#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         (('0.0.0.0', port))
#         sock.listen(100)
#         print(f'SSH running on :{port}...')
#     except Exception as e:
#         print(f'ae ssh error: {e}')
# 
#     while True:
#         try:
#             client_socket, addr = sock.accept()
#             print(f'Connection from {addr[0]}:{addr[1]}')
#             # Handle each connection in a new thread
#             client_thread = threading.Thread(target=handle_connection, args=(client_socket,))
#             client_thread.start()
#         except Exception as e:
#             print(f'*** Error accepting connection: {e}')

class HostCommunication:

    def getnic():
        global localip
        logprint("getnic()")
        csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csFT.connect((localip, 8750))
        # Send command
        csFT.send(b"getnic")
        logprint("Command sent! Waiting...")
        data = csFT.recv(1024)
        decoded = data.decode('utf-8')
        logprint("Data from client recived")
        logprint(decoded)
        return decoded

    def getclientinfo():
        global localip
        logprint("getclientinfo()")
        csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csFT.connect((localip, 8750))
        # Send command
        csFT.send(b"getsys")
        logprint("Command sent! Waiting...")
        data = csFT.recv(1024)
        decoded = data.decode('utf-8')
        logprint("Data from client recived")
        logprint(decoded)
        cpuname = decoded
        thelist = cpuname.split("|eilo|")
        logprint(thelist)
        logprint("Success")
        cpu = thelist[0]
        os = thelist[1]
        release = thelist[2]
        build = thelist[3]
        hostname = thelist[4]
        cores = thelist[5]
        procid = thelist[6]
        arch = thelist[7]
        percentram = thelist[8]
        totalram = thelist[9]
        usagecpu = thelist[10]
        # returns 8 variables
        time.sleep(0.1)
        logprint("Complete! Sending back 'ae' to your client...")
        csFT.send(b"ae") # let client know that we good
        time.sleep(0.1)
        return cpu,os,release,build,hostname,cores,procid,arch,percentram,totalram,usagecpu
    
    def getclientscreenshot():
        global localip
        csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csFT.connect((localip, 8750))
        # get a screenshot from client
        csFT.send(b"getscr")
        logprint("Command sent! Waiting...")
        with open("clientscreenshot.png",'wb') as scr:
            while True:
                #logprint("Now listening for screenshot data.")
                data = csFT.recv(1024)
                #logprint(data)
                if data == b"aeeiloae":
                    logprint("Data completed, ae recived")
                    break
                if not data:
                    logprint("Data sent over complete")
                    break
                scr.write(data)
            logprint("Successfully transfered screenshot")
            scr.close()
            # send back an ae
            time.sleep(0.1)
            return 1

    def oembdi_ping(ipaddr):
        global localip
        logprint(f"Wants to ping: {ipaddr}")
        csFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csFT.connect((localip, 8750))
        # get a screenshot from client
        csFT.send(b"initping")
        # client pings the given
        data = csFT.recv(1024)
        if data == b"can i haz ip?":
            csFT.send(f"sure! ping this ip:{ipaddr}".encode('utf-8'))
        data = csFT.recv(1024) # wait till ping completes
        # get results




# management class
class EiLO:

    def getuserfromip(ip):
        # get username from the ip address (logged in users)
        global authusers
        global authenticatedAddresses
        username = ""
        for i in range(len(authenticatedAddresses)):
            ipaddr = authenticatedAddresses[i]
            if ipaddr == ip:
                username = authusers[i]
        return username
    
    def getipfromuser(username):
        # get the ip address from username (logged in users)
        global authusers
        global authenticatedAddresses
        ip = ""
        for i in range(len(authusers)):
            users = authusers[i]
            if users == username:
                ip = authenticatedAddresses[i]
        return ip
    
    def deleteuser(username):
        if username == "Administrator":
            logprint("Cant delete the default user")
            return 0
        logprint("Deleting: ",username)
        global users
        global paswds
        global permissions
        global authenticatedAddresses
        global authusers
        # purge from users and pswds
        for i in range(len(users)):
            if users[i] == username:
                # found it.
                # deleting...
                users.remove(username)
                password = paswds[i]
                paswds.remove(password)
                logprint(f"User {username} Deleted successfully")
                EventLog.eventwrite(f"User {username} Deleted successfully")
                permission = permissions[i]
                permissions.remove(permission)
                configuration.updateaccounts()
                logprint("User deletion complete")
                break
        try:
            for i in range(len(authusers)):
                if authusers[i] == username:
                    logprint("That user was logged on too, Signing him off")
                    ipaddr = authenticatedAddresses[i]
                    authenticatedAddresses.remove(ipaddr)
                    userspot = authusers[i]
                    authusers.remove(userspot)
                    logprint("Success")
        except:
            logprint(f"{username} was not logged in over http")


    def signout(username):
        global authenticatedAddresses
        global authusers
        try:
            for i in range(len(authusers)):
                if authusers[i] == username:
                    ipaddr = authenticatedAddresses[i]
                    authenticatedAddresses.remove(ipaddr)
                    userspot = authusers[i]
                    authusers.remove(userspot)
                    logprint(f"{username} signed out")
                    EventLog.eventwrite(f"User {username} Signed out of HTTP")
        except:
            logprint(f"Could not sign off {username}")
        

    def getuserslist():
        # get the list of all users (parsed)
        global users
        mainstring = ""
        for i in range(len(users)): # Subtract 1 from len to skip over default user
            username = users[i]
            if mainstring != "":
                mainstring = f"{mainstring}{username}|eilo|"
            else:
                # first user
                mainstring = f"{username}|eilo|"
        logprint(mainstring)
        return mainstring 
    def getpermsuser(username,givevars=0):
        # get parsed string and vars of the 5 perms of a certain user ae
        global users
        global permissions
        if username != "":

            theindex = 0
            mainstring = ""
            for i in range(len(users)): # Subtract 1 from len to skip over default user
                if users[i] == username:
                    theindex = i
            userperms = permissions[theindex]
            thesplit = userperms.split(",")
            http = thesplit[0]
            irc = thesplit[1]
            virt = thesplit[2]
            pwer = thesplit[3]
            sett = thesplit[4]
            admin = thesplit[5]
            # 1|eilo|1|eilo|1|eilo|1|eilo|1|eilo|1
            parsed = f"{http}|eilo|{irc}|eilo|{virt}|eilo|{pwer}|eilo|{sett}|eilo|{admin}"
            if givevars == 1:
                return http,irc,virt,pwer,sett,admin
            else:
                return parsed
        else:
            mainstring = ""
            for i in range(len(users)): # Subtract 1 from len to skip over default user
                username = users[i]
                if mainstring != "":
                    # new user in perms list
                    mainstring = f"{mainstring}{permissions[i]}|eilo|" 
                else:
                    mainstring = f"{permissions[i]}|eilo|"
                #if users[i] == username:

                #    theindex = i
            logprint(mainstring)
            return mainstring

    def checkauth(ip,hasperm=""):
        global authenticatedAddresses
        global authusers
        global permissions
        global users
        ipindex = 0
        authuserindex = 0
        permindex = -1
        userindex = -1
        if ip in authenticatedAddresses and hasperm == "":
            return 1
        elif ip in authenticatedAddresses and hasperm != "":
            logprint("perm check")
            # first get the indexes
            for i in range(len(authenticatedAddresses)):
                if ip == authenticatedAddresses[i]:
                    ipindex = i
                    authuserindex = i # ip addr maps into authusers
            for ae in range(len(users)):
                testname = users[ae]
                logprint("testname: ",testname)
                logprint(authenticatedAddresses)
                logprint(authusers)
                logprint("ae: ",ae)
                if userindex == -1:
                    if len(authusers) == 1:
                        if testname == authusers[0]:
                            # found the index
                            logprint("Found userindex")
                            userindex = ae
                            permindex = ae
                    else:
                        for aee in range(len(authusers)): # check them one by one xd
                            if testname == authusers[aee]:
                                # found the index
                                logprint("Found userindex")
                                userindex = ae
                                permindex = ae
                            
            if hasperm == "http":
                perm = 0
            if hasperm == "irc":
                perm = 1         
            if hasperm == "virt":
                perm = 2
            if hasperm == "pwer":
                perm = 3
            if hasperm == "sett":
                perm = 4
            if hasperm == "admin":
                perm = 5
            # finally, check if has permission
            permstring = permissions[permindex]
            permstring = permstring.split(",")
            logprint(permstring)
            if permstring[perm] == "1":
                # Permission!
                logprint("checkauth(): perm applies!")
                logprint("full permission list: ",permissions)
                return 1
            else:
                # illegal attempt!
                logprint("checkauth(): failure! user no perm!")
                return 0
        else:
            return 0

    def usersession(ip,username):
        logprint(f"Adding ip: {ip} to the list of authenticated sessions")
        global authenticatedAddresses
        global authusers
        authenticatedAddresses.append(ip)
        authusers.append(username)
        logprint("Session added")
        EventLog.eventwrite(f"IP Address {ip} has been given a new session")
        logprint(authenticatedAddresses)
        time.sleep(3600)
        EventLog.eventwrite(f"Session for {ip} (username: {username}) has ended (timed out, 1hr, 3600 seconds)")
        # Session ended.
        authenticatedAddresses.remove(ip)
        authusers.remove(username)
        logprint(authenticatedAddresses)

    def casheuser(ip,username):
        printlog(f"IP Address {ip} was cashed into the system under the username: {username}")
        global authenticatedAddresses 
        logprint(ip)
        if ip in authenticatedAddresses:
            logprint(f"{ip} is already cashed!")
        else:
            auththread = threading.Thread(target=EiLO.usersession, args=(ip,username,))
            auththread.start()

    def testprint(st):
        logprint(st)

    def authenticateUser(ip,username="",password=""):
        global users
        global paswds
        global authenticatedAddresses
        userfound = 0
        paswfound = 0
        amntuser = len(users)
        amntpasw = len(paswds)
        # check standard lists
        for i in range(amntuser): 
            if username == users[i]:
                userfound = 1
        for i in range(amntpasw): 
            if password == paswds[i]:
                paswfound = 1
            
        if userfound and paswfound == 1:
            logprint("User logged in succesfully!")
            EventLog.eventwrite(f"IP Address {ip} authenticated successfully")
            EiLO.casheuser(ip,username)
            return 1
        elif ip in authenticatedAddresses:
            logprint("IP Address in auth list!")
            return 1
        # Not logged in
        return 0
    
    def powermomentary(ip):
        perm = EiLO.checkauth(ip,"pwer")
        if perm == 1:
            global powerstate
            if powerstate == 1:
                powerstate = 3
            if powerstate == 0:
                powerstate = 2
            writeserialdata(b"A")
            printlog("Power momentary given from WebUI")
    def powerhold(ip):
        perm = EiLO.checkauth(ip,"pwer")
        if perm == 1:
            writeserialdata(b"B")
            global powerstate
            if powerstate == 1:
                powerstate = 3
            printlog("Power hold given from WebUI")
    def powerreset(ip):
        perm = EiLO.checkauth(ip,"pwer")
        if perm == 1:
            global powerstate
            if powerstate == 1:
                powerstate = 2
            printlog("Power reset given from WebUI")
            writeserialdata(b"C")
    def powercoldboot(ip):
        perm = EiLO.checkauth(ip,"pwer")
        if perm == 1:
            global powerstate
            if powerstate == 1:
                powerstate = 2
            printlog("Power cold boot given from WebUI")
            writeserialdata(b"B")
            time.sleep(15)
            writeserialdata(b"A")


# Webserver Class
class Serv(BaseHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        # Modified version of 
        global debug
        if debug == 1:
            self.log_message('"%s" %s %s',self.requestline, str(code), str(size))

    def do_GET(self):
        # globals
        global motd
        global localip
        global computername
        global longcomputername
        global httpport
        global virport
        global cliport
        global terminalport
        global mgmthostname
        logprint(f"new message from {self.address_string()}")
        if self.path == '/':
            self.path = '/index.html'
        allowed = EiLO.checkauth(self.address_string(),"http")
        # Auth check
        if self.path != '/index.html' and self.path != '/' and self.path != '/login.html' and self.path != '/motd' and self.path != '/smallinfo' and self.path != '/remo':
            if allowed == 0:
                self.path = '/unauth.html'
                self.send_response(401)
               # printlog(f"Unauthorized (401) was given out to: {self.address_string()}")

        if self.path == '/iloconfig.txt':
            self.path = '/forb.html'
            self.send_response(403)
            printlog(f"Forbidden (403) was given out to: {self.address_string()} They attempted to access iloconfig through the webgui")
            return 0

        # Power stuff
        if self.path == '/powermomentary' and allowed == 1:
            EiLO.powermomentary(self.address_string())
        if self.path == '/powerhold' and allowed == 1:
            EiLO.powerhold(self.address_string())
        if self.path == '/powercold' and allowed == 1:
            EiLO.powercoldboot(self.address_string())
        if self.path == '/powerreset' and allowed == 1:
            EiLO.powerreset(self.address_string()) 

        try: 
            ae = f"{self.path}"
            ae = ae[1:]
            logprint(ae)
            logprint(self.path)
            file_to_open = open(ae,'r').read()
            self.send_response(200)
            #UserMangement.testlogprint("aeaaaaaa")
        except:
            # custom urls 
            if self.path == "/overview.get":
                cpu,os,release,build,hostname,cores,procid,arch,percentram,totalram,usagecpu = HostCommunication.getclientinfo()
                fullstring = f"{cpu}|{os}|{release}|{build}|{hostname}|{cores}|{procid}|{arch}|{percentram}|{totalram}|{usagecpu}|{computername}|{longcomputername}|{localip}"
                file_to_open = fullstring
                self.send_response(200)
            elif self.path == "/usersget":
                thestring = EiLO.getuserslist()
                file_to_open = thestring
                self.send_response(200)
            elif self.path == "/signout":
                EiLO.signout(EiLO.getuserfromip(self.address_string()))
                EventLog.eventwrite(f"User {EiLO.getuserfromip(self.address_string())} has signed out from UI. IP Address: {self.address_string()}")
                try:
                    ae = f"/so.html"
                    ae = ae[1:]
                    file_to_open = open(ae,'r').read()
                except:
                    file_to_open = "Signed out!\nYou may now close this tab."
                time.sleep(1)
                self.send_response(200)
            elif self.path == "/permsget":
                thestring = EiLO.getpermsuser("",)
                file_to_open = thestring
                self.send_response(200)
            elif self.path == "/eventlog":
                logarray,logstring = EventLog.geteventlog(1)
                logstring = f"<html>{logstring}</html>" # give a nice formated http eventlog
                file_to_open = logstring
                self.send_response(200)

            # Temp screenshot alias
            elif self.path == "/powerstate":
                file_to_open = getpowerstate()
                self.send_response(200)

            elif self.path == "/tempscr.png":
                logprint("screenshot request via http!")
                if getpowerstate() == "ON":
                    time.sleep(2)
                    HostCommunication.getclientscreenshot()
                    file_to_open = open('clientscreenshot.png','rb').read()
                else:
                    # server is off
                    file_to_open = open('offlinesrc.png','rb').read()
                self.send_response(200)
            # ports
            elif self.path == "/http":
                ae = f"{httpport}".encode('utf-8')
                file_to_open = ae 
                self.send_response(200)
            elif self.path == "/virt":
                ae = f"{virport}".encode('utf-8')
                file_to_open = ae
                self.send_response(200)
            elif self.path == "/clie":
                ae = f"{cliport}".encode('utf-8')
                file_to_open = ae
                self.send_response(200)
            elif self.path == "/remo":
                ae = f"{terminalport}".encode('utf-8')
                file_to_open = ae
                self.send_response(200)

            elif self.path == "/motd":
                file_to_open = motd
                self.send_response(200)
            elif self.path == "/irc.exe":
                file_to_open = open("IRC.exe",'rb').read()
                self.send_response(200)

            elif self.path == "/smallinfo":
                file_to_open = longcomputername + " -- " + computername
                self.send_response(200)
            elif self.path == "/servername":
                file_to_open = computername
                self.send_response(200)

            elif self.path == "/hostname":
                file_to_open = mgmthostname
                self.send_response(200)

            elif self.path == "/localip":
                file_to_open = localip
                self.send_response(200)


            else:
                file_to_open = "File not found"
                self.send_response(404)
        self.end_headers()
        try:
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        except:
            self.wfile.write(file_to_open)
    

    def do_POST(self):
        logprint ("got a POST request.")
        if self.path == '/login.html':
            logprint("The POST request is for the login system.")
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            logprint("MY SERVER: The post data I received from the request has following data:\n", post_data_bytes)

            post_data_str = post_data_bytes.decode("UTF-8")
            post_data_list = post_data_str.split("=")
            logprint([post_data_list])

            uname = post_data_list[1]
            unamestr1 = uname.split('"uname"\r\n\r\n')
            logprint(f"\n\n{unamestr1}\n\n")
            unamelist2 = unamestr1[1]
            uname2 = unamelist2.split("\r\n")
            unamemain = uname2[0]
            logprint(f"\n\nUsername: |{unamemain}| - end username")
            psw = post_data_list[2]
            pswstr1 = psw.split('"psw"\r\n\r\n')
            logprint(f"\n\n{pswstr1}\n\n")
            pswlist2 = pswstr1[1]
            psw2 = pswlist2.split("\r\n")
            pswmain = psw2[0]
            logprint(f"\n\nPassword: |{pswmain}| - end password")
            logprint(f"Login request from {self.address_string()}")
            logprint(f"eilo{pswmain}eilo")
            logprint(f"eilo{unamemain}eilo")
            authenticated = EiLO.authenticateUser(self.address_string(),unamemain,pswmain)
            if authenticated == 1:
                logprint("redirected!")
                self.path = '/redir.html'


        # ports update
        logprint ("got a POST request.")
        if self.path == '/accessports.html':
            content_length = int(self.headers['Content-Length'])
            post_data_bytes = self.rfile.read(content_length)
            logprint("MY SERVER: The post data I received from the request has following data:\n", post_data_bytes)

            post_data_str = post_data_bytes.decode("UTF-8")
            post_data_list = post_data_str.split("=")
            logprint([post_data_list])
#id="webserver
#id="virtmedia
#id="clientapp
#id="remotecon
            webserver = post_data_list[1]
            webserverstr1 = webserver.split('"webserver"\r\n\r\n')
            logprint(f"\n\n{webserverstr1}\n\n")
            webserverlist2 = webserverstr1[1]
            webserver2 = webserverlist2.split("\r\n")
            webservermain = webserver2[0]
            logprint(f"\n\nwebserverport: |{webservermain}| - end port")
            #psw = post_data_list[2]
            #pswstr1 = psw.split('"psw"\r\n\r\n')
            #logprint(f"\n\n{pswstr1}\n\n")
            #pswlist2 = pswstr1[1]
            #psw2 = pswlist2.split("\r\n")
            #pswmain = psw2[0]
            #logprint(f"\n\nPassword: |{pswmain}| - end password")
            #logprint(f"Login request from {self.address_string()}")
            #logprint(f"eilo{pswmain}eilo")
            #logprint(f"eilo{unamemain}eilo")
            #authenticated = EiLO.authenticateUser(self.address_string(),unamemain,pswmain)
            #if authenticated == 1:
            #    logprint("redirected!")
            #    self.path = '/redir.html'


        if self.path == '/newuser.html':
            allowed = EiLO.checkauth(self.address_string(),"admin")
            if allowed == 1:
                logprint("The POST request is for the login system.")
                content_length = int(self.headers['Content-Length'])
                post_data_bytes = self.rfile.read(content_length)
                logprint("MY SERVER: The post data I received from the request has following data:\n", post_data_bytes)

                post_data_str = post_data_bytes.decode("UTF-8")
                post_data_list = post_data_str.split("=")
                logprint([post_data_list])
                logprint("Length of postdatalist: ",len(post_data_list))
                uname = post_data_list[1]
                unamestr1 = uname.split('"uname"\r\n\r\n')
                logprint(f"\n\n{unamestr1}\n\n")
                unamelist2 = unamestr1[1]
                uname2 = unamelist2.split("\r\n")
                unamemain = uname2[0]
                logprint(f"\n\nUsername: |{unamemain}| - end username")

                psw = post_data_list[2]
                pswstr1 = psw.split('"psw"\r\n\r\n')
                logprint(f"\n\n{pswstr1}\n\n")
                pswlist2 = pswstr1[1]
                psw2 = pswlist2.split("\r\n")
                pswmain = psw2[0]
                logprint(f"\n\nPassword: |{pswmain}| - end password")
                http = 0
                irc  = 0
                virt = 0
                pwer = 0
                sett = 0
                admin= 0


                for i in range(len(post_data_list) - 2): # sub user and pass
                    logprint("Looking for perm: HTTP")
                    # find & check http perm
                    perm = post_data_list[i + 2]
                    permstr1 = perm.split('"http"\r\n\r\n') # looking for "http"
                    logprint(f"\n\nHeres the perm:\n{permstr1}\n\n")
                    logprint(f"len of that perm!: {len(permstr1)}")
                    if len(permstr1) > 1:
                        logprint("HTTP perm is present!")
                        http = 1
                for i in range(len(post_data_list) - 2): # sub user and pass
                    logprint("Looking for perm: IRC")
                    # find & check irc perm
                    perm = post_data_list[i + 2]
                    permstr1 = perm.split('"irc"\r\n\r\n')
                    logprint(f"\n\nHeres the perm:\n{permstr1}\n\n")
                    logprint(f"len of that perm!: {len(permstr1)}")
                    if len(permstr1) > 1:
                        logprint("IRC perm is present!")
                        irc = 1
                for i in range(len(post_data_list) - 2): # sub user and pass
                    logprint("Looking for perm: VIRT")
                    # find & check irc perm
                    perm = post_data_list[i + 2]
                    permstr1 = perm.split('"virt"\r\n\r\n')
                    logprint(f"\n\nHeres the perm:\n{permstr1}\n\n")
                    logprint(f"len of that perm!: {len(permstr1)}")
                    if len(permstr1) > 1:
                        logprint("VIRT perm is present!")
                        virt = 1
                for i in range(len(post_data_list) - 2): # sub user and pass
                    logprint("Looking for perm: pwer")
                    # find & check virt perm
                    perm = post_data_list[i + 2]
                    permstr1 = perm.split('"pwer"\r\n\r\n')
                    logprint(f"\n\nHeres the perm:\n{permstr1}\n\n")
                    logprint(f"len of that perm!: {len(permstr1)}")
                    if len(permstr1) > 1:
                        logprint("PWER perm is present!")
                        pwer = 1
                for i in range(len(post_data_list) - 2): # sub user and pass
                    logprint("Looking for perm: sett")
                    # find & check virt perm
                    perm = post_data_list[i + 2]
                    permstr1 = perm.split('"sett"\r\n\r\n')
                    logprint(f"\n\nHeres the perm:\n{permstr1}\n\n")
                    logprint(f"len of that perm!: {len(permstr1)}")
                    if len(permstr1) > 1:
                        logprint("SETT perm is present!")
                        sett = 1
                for i in range(len(post_data_list) - 2): # sub user and pass
                    logprint("Looking for perm: admin")
                    # find & check virt perm
                    perm = post_data_list[i + 2]
                    permstr1 = perm.split('"admin"\r\n\r\n')
                    logprint(f"\n\nHeres the perm:\n{permstr1}\n\n")
                    logprint(f"len of that perm!: {len(permstr1)}")
                    if len(permstr1) > 1:
                        logprint("ADMIN perm is present!")
                        admin = 1
                logprint("\nFinal permission list!")
                logprint(f"HTTP: {http} | IRC: {irc} | VIRT: {virt} | PWER: {pwer} | SETT: {sett} | ADMIN: {admin}")
                permstring = f"{http},{irc},{virt},{pwer},{sett},{admin}"
                global users
                global paswds
                global permissions
                cancontinue = 1
                for i in range(len(users)):
                    if users[i] == unamemain:
                        logprint("This username is already taken!")
                        self.path = '/taken.html'
                        cancontinue = 0
                if cancontinue == 1:
                    logprint(f"\n\n\nCreating account: {unamemain}\n\nPermissions: {permstring}\n\n\n")
                    users.append(unamemain)
                    paswds.append(pswmain)
                    permissions.append(permstring)
                    logprint("\n\naccounts updated:\n\n")
                    logprint(users)
                    logprint(paswds)

                    time.sleep(2)
                    configuration.updateaccounts()
                    self.path = '/success.html'


           #    http = post_data_list[3]
           #    httpstr1 = http.split('"http"\r\n\r\n')
           #    logprint(f"\n\n{httpstr1}\n\n")
           #    httplist2 = httpstr1[1]
           #    http2 = httplist2.split("\r\n")
           #    httpmain = http2[0]
           #    logprint(f"\n\nHTTP perm: {httpmain} - end http perm")

                #logprint(f"Login request from {self.address_string()}")
                #logprint(f"eilo{pswmain}eilo")
                #logprint(f"eilo{unamemain}eilo")
                #authenticated = EiLO.authenticateUser(self.address_string(),unamemain,pswmain)
                #if authenticated == 1:
                #    logprint("redirected!")
                #    self.path = '/redir.html'
            else:
                logprint("Someone tried to create a user without perms!")
                printlog(f"{self.address_string()} Attempted to create a user with insuffciant permissions")
                logprint("redirected!")
                self.path = '/unauth.html'
        return Serv.do_GET(self)
 
 




def starthttp():
    global httpport
    print(f"Starting HTTP Server on port: {httpport}") 
    EventLog.eventwrite(f"Starting HTTP Server on port: {httpport}")
    httpd = ThreadingHTTPServer(("0.0.0.0",httpport),Serv)
    httpd.serve_forever()
httpserver = threading.Thread(target=starthttp, args=())
httpserver.start()






# arguement parser
# compatible with linux only atm (I use a raspberry pi to connect up to the Arduino)
connected = 1
# Moved! Moved to writeserialdata(b'command here')


# Remote Console Session
# [0] is the prompt
# [1] is the reset of the message


# Todo: Improve this function to accept more connections keeping port chanaging a minimum
def remoteconsole(port):
    print(f"\nRemote Console Port: {port}")
    loggedin = 0
    isconnected = 0
    global password
    global computername
    while True:
        # get the hostname
        host = "0.0.0.0" # socket.gethostname()
        print("Starting Remote Console Server")
        logprint(host)
        logprint(port)
        rcusername = ""
        rcpassword = ""
        server_socket = socket.socket()  # get instance
        global devconsetup
        server_socket.bind((host, port))  # bind host address and port together
        devconsetup = 1
        # configure how many client the server can listen simultaneously
        server_socket.listen(2)
        conn, address = server_socket.accept()  # accept new connection
        logprint("log: new remote console from: " + str(address))
        # open a new connection!
        #newport = port + 1 # increase the next port by one so more connections can be made after
        #aex = threading.Thread(target=remoteconsole, args=(newport,))
        #aex.start()
        while True:
            new = 0
            # if this is the second loop:
            if isconnected == 1:
                if loggedin == 0:
                    message = "NONE&&login as: "
                    conn.send(message.encode())
                    try:
                        data = conn.recv(1024).decode() # Get response
                        datastr = str(data)
                        thesplit = datastr.split("&&")
                        rcusername = thesplit[1]
                        # === new! ===
                        # convert to useraccount system
                        index = -1
                        global users
                        global paswds
                        for i in range(len(users)):
                            if users[i] == rcusername:
                                # user exists!!
                                index = i
                        

                        message = f"NONEPASS&&password for {thesplit[1]}: "
                        conn.send(message.encode())
                        data = conn.recv(1024).decode() # Get response
                        datastr = str(data)
                        thesplit = datastr.split("&&")
                        rcpassword = thesplit[1]
                        if index == -1:
                            # no user account
                            conn.close()
                            logprint("breaking...")
                            break
                        
                        if str(rcpassword) == str(paswds[index]):
                            # check the permissions of the user
                            logprint("that password works, getting permissions")
                            http,irca,virt,pwer,sett,admin = EiLO.getpermsuser(rcusername,1)
                            logprint(f'IRCA:{irca}:IRCA')
                            if irca == 1 or irca == "1" or irca == " 1" or irca == "1 " or irca == " 1 ":
                                loggedin = 1 
                                logprint("Remote console user authenticated successfully")
                                message = f"<{rcusername}>@{computername}_EiLO $ &&EiLO 3 build 188 at Dec 06 2025\nSystem Name: {computername}\nSystem Power: {getpowerstate()}\n&&cls"
                                conn.send(message.encode())   
                            else: 
                                logprint("no irc perm")
                                message = f">&&Your user account does not have the nessory permissions to use the Remote Console\nPlease consult your Administrator&&exit"
                                conn.send(message.encode())  
                    except Exception as e:
                        logprint(f"Exception on remote console login\n{e}")
                        logprint("A device disconnected! (From exception detect)")
                        conn.close()
                        logprint("Disconncted!!!")
                        #aex = threading.Thread(target=remoteconsole, args=(port,))
                        #aex.start()
                        break
            # receive data stream. it won't accept data packet greater than 1024 bytes
            try:
                data = conn.recv(1024).decode() # This line errors when a client disconnects.
            except:
                logprint("A device disconnected! Device list cleared.")
                conn.close()
                logprint("Disconncted!!!")
                #aex = threading.Thread(target=remoteconsole, args=(port,))
                #aex.start()
                break

            if not data:
                # if data is not received break
                ae = 0
            if data != '':
                if str(data) != "ae":
                    logprint("\nRemote Console: from a client: " + str(data))
                    datastr = str(data)
                    thesplit = datastr.split("&&")
                    logprint(f"datastr:{datastr}")
                    devicename = thesplit[0]
                    text = thesplit[1]
                    logprint(thesplit)
                    if thesplit[1] == " Command recived\n": # This is the message the device first sends. initing the sequense
                        logprint(f"log: New device connected to remote console | {devicename}")
                        isconnected = 1
                        # End here. go to login script at top
                    if loggedin == 1:
                        prompt, messageback = parsecommand(rcusername,thesplit[1])

                        logprint(prompt)
                        logprint(messageback)
                        message = f"{prompt}&&{messageback}"
                        conn.send(message.encode())   
                        if thesplit[1] == "exit":
                            time.sleep(1)
                            conn.close()
            new = 1
            while new == 1:
                new = 0
            data = ''
        logprint("Breaking out of that while loop #1")
        break
    logprint("Out of the while loop!")
    conn.close()
    logprint("remoteconsole() function thread exited successuflly!!")
    aex = threading.Thread(target=remoteconsole, args=(port,))
    aex.start()

print("Starting Remote Console Server...")
telnet = threading.Thread(target=remoteconsole, args=(terminalport,))
telnet.start()

# Discord
token = dct
import discord, asyncio, os, time
from discord.ext import commands
loop = asyncio.get_event_loop()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
@bot.command()
async def commandlist(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send("EiLO help")
    await ctx.send("power <type>      Performs an action on the Power Button")
    await ctx.send("  |---power momentary   Press the Power button once")
    await ctx.send("  |---power hold        Press and hold the Power button for 5 seconds (Will force shutdown)")
    await ctx.send("  |---power coldboot    Power hold followed by momentary. Resulting in a cold boot")
    await ctx.send("  |---power reset       Reset the system")
    await ctx.send("Short commands\n  |---power on       Turn on the system")
    await ctx.send("  |---power off       Logically power off the system")
    await ctx.send("")
    await ctx.send("End Help")



@bot.command()
async def test(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f'{len(args)} arguments: {arguments}')
@bot.command()
async def power(ctx, *, cmd):
    if cmd == "momentary":
        writeserialdata(b"A")
        await ctx.send(f"`Command Executed Successfully`")
    if cmd == "hold":
        writeserialdata(b"B")
        await ctx.send(f"`Command Executed Successfully`")
    if cmd == "reset":
        writeserialdata(b"C")
        await ctx.send(f"`Command Executed Successfully`")
@bot.command()
async def version(ctx, *args):
    await ctx.send(f"Externally-Integrated Lights Out Version 3.0 (*build 188*)\nCode Written by Phoenix - Scarface 1")
#bot.add_command(test)
def botthread(): 
    loop.create_task(bot.start(f"{token}"))# R3

    try:
        if token != "NONE":
            print("Starting discord bot...")
            loop.run_forever()
            print("Bot running")
        else:
            print("Discord Bot Disabled")
    except:
        loop.stop()
dcbot = threading.Thread(target=botthread, args=())
dcbot.start()



# System Information Class
 
class SysInfo:
    def pinghost(pings=1):
        global localip # The systems IP Address
        host = localip
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, str(pings), host] # Only ping once
        return subprocess.call(command,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.STDOUT) == 0
    
    def pingloop():
        while True:
            global powerstate
            #print("ping loop!")
            time.sleep(5)
            # This function is to determine when the Server is on and when its not on.
            # Ping the system
            pingresult = SysInfo.pinghost()
            #print(powerstate)
            if powerstate == 3:
                # Shutdown in progress
                if pingresult == 1:
                    powerstate = 3
                else:
                    logprint("Host System Offline!")
                    EventLog.eventwrite(f"Host System Offline!")
                    powerstate = 0

            if powerstate == 2:
                # Startup in progress...
                if pingresult == 1:
                    powerstate = 1
                    logprint("Host System Online!")
                    EventLog.eventwrite(f"Host System Online!")
                else:
                    powerstate = 2 # System bootup in progress
            if powerstate == 1: # System was on before
                if pingresult == 0: # Cant reach it
                    logprint("Host System Offline!")
                    EventLog.eventwrite(f"Host System Offline!")
                    powerstate = 0
            if powerstate == 0: # System was off before
                if pingresult == 1: # Cant reach it
                    logprint("Host System Online!")
                    EventLog.eventwrite(f"Host System Online!")
                    powerstate = 1


    def determineInitalPowerState():
        global powerstate
        global localip
        EventLog.eventwrite(f"Determining Host Status...")
        print("Determining Host Status...")
        pingresult = SysInfo.pinghost(6) # try to contact the host a few times (This command is linux compatible!!)
        if pingresult == 1:
            powerstate = 1
            print("EiLO 3 detected that the Host System is ON.")
            EventLog.eventwrite(f"EiLO 3 detected that the Host System is ON.")
        else:
            powerstate = 0
            print("EiLO 3 detected that the Host System is OFF.")
            EventLog.eventwrite(f"EiLO 3 detected that the Host System is OFF.")
            ans = input("Is this correct? (y/n)> ")
            if ans == "y":
                powerstate == 0
            if ans == "n":
                powerstate == 2
                print(f"Unable to determine power status of the Host! Cant ping {localip}\nPower state set to bootup in progress")
        powerloop = threading.Thread(target=SysInfo.pingloop, args=())
        powerloop.start()


# Live Console Session

printlog(f"{computername} | New EiLO Console Session Initiated")



phnyautostartThread = threading.Thread(target=phnyautostart, args=())
phnyautostartThread.start()
print("PhnyAutoStart is currently disabled. To enable it, check out the autostart command")
SysInfo.determineInitalPowerState()
while True:
    print("--- INIT Local EiLO 3 Console Session ---")
    pswd = str(getpass("EiLO3 password: "))
    if pswd == password:
        print("")
        print("EiLO 3 build 190 at Feb 10 2026")
        print("Welcome back, Administrator!")
        print(f"System Name: {computername}")
        print(f"System Power: {getpowerstate()}")
        print(f"Type help for a list of commands\n")
        
        printlog(f"{computername} | Local Console | User authenticated using EiLO Master password (Success)")
        while True:
            command()
    if pswd != password:
        time.sleep(3)
        print("Password Failure")
        printlog(f"{computername} | Local Console | Password Failure Log: {pswd}")
