# This is EiLOs Client Code (This code runs on the device EiLO controls)
import socket, time, platform, os, multiprocessing, cpuinfo, netifaces
# pip install py-cpuinfo
import psutil
from mss import mss
print("Hello from Client (Client of EiLO3)")
def main():
    ssFT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssFT.bind((socket.gethostname(), 8750))
    ssFT.listen(1)
    print("Connection ready!")
    while True:
        print("Now listening for a command from EiLO")
        (conn, address) = ssFT.accept()
        data = conn.recv(1024) # Listen for a new command
        print('Received From Server: ', data.decode('utf-8'))
        decoded = data.decode('utf-8')
        print(f"eilo{decoded}eilo")
        print(data)
        print(decoded)
        print("Parsing...")
        if decoded == "getnic":
            # network
            if os.name == 'nt':
                print("ae")
        elif decoded == "getsys":
            print("Request made for system info")
            usagecpu = psutil.cpu_percent() 
            uname = platform.uname()
            os = uname.system
            hostname = uname.node
            release = uname.release
            build = uname.version
            if os == "Windows":
                os = f"Windows {release}"
                print(f"{os} build {build}")
            arch = uname.machine
            procid = uname.processor
            pyver = platform.python_version()
            ram = psutil.virtual_memory().percent
            totalram = psutil.virtual_memory().total
            time.sleep(1) 
        #print(f"This Systems CPU Usage: {psutil.cpu_percent(interval=None)}%")
        #usage = f"CPU Activity {psutil.cpu_percent(interval=None)}%"
            cores = multiprocessing.cpu_count()
            cpustuff = cpuinfo.get_cpu_info()
            print(cpustuff)
            cpuname = cpustuff["brand_raw"]
            print("CPU Name: ",cpuname)
            print(f"System: {uname.system}")
            print(f"Node Name: {uname.node}")
            print(f"Release: {uname.release}")
            print(f"Version: {uname.version}")
            print(f"Machine: {uname.machine}")
            print(f"Processor: {uname.processor}")
            print(f"Python Version: {platform.python_version()}")
        # send information back!
            parsedstring = f"{cpuname}|eilo|{os}|eilo|{release}|eilo|{build}|eilo|{hostname}|eilo|{cores}|eilo|{procid}|eilo|{arch}|eilo|{ram}|eilo|{totalram}|eilo|{usagecpu}"
            conn.send(f"{parsedstring}".encode('utf-8')) # transmit data from client to EiLO
            data2 = conn.recv(1024) # important, Wait for ready to disconnect
            data2 = data2.decode('utf-8')
            time.sleep(0.5) # wait a little longer than server
            if data2 == "ae":
                ssFT.close()
                break
        elif decoded == "getscr":
            print("Server wants a screenshot!")
            try:
                with mss() as sct:
                    sct.shot(mon=0, output='eiloscreen.png')
                time.sleep(1)
                with open("eiloscreen.png",'rb') as scr:
                    while True:
                        data = scr.read(1024)
                        #print("Sending screenshot snippet data!")
                        #print(data)
                        conn.send(data) # send the snippet of data
                        #print("That data got sent successfully!")
                        if not data:
                            print('Thats the end of the screenshot file, all data sent!')
                            time.sleep(0.1)
                            conn.close()
                            break
                    scr.close()
                    print("Screenshot sent complete!")
                    break
            except:
                print("Running headless!")
                time.sleep(1)
                try:
                    with open("headless.png",'rb') as scr:
                        while True:
                            data = scr.read(1024)
                            #print("Sending screenshot snippet data!")
                            #print(data)
                            conn.send(data) # send the snippet of data
                            #print("That data got sent successfully!")
                            if not data:
                                print('Thats the end of the screenshot file, all data sent!')
                                time.sleep(0.1)
                                conn.close()
                                break
                        scr.close()
                        print("Screenshot sent complete!")
                        break
                except:
                    conn.close()
                    break
            
           # ssFT.close()
        elif decoded == "initping":
            conn.send(b"can i haz ip?")
            ipaddr = conn.recv(1024)
            ipaddr = ipaddr.decode('utf-8')
            ipaddr = ipaddr.split(':')
            ipaddr = ipaddr[1]
            print(f"Pinging: {ipaddr}")
            
            

                    
    #
    #conn.send(b"ae")
    #
while True:
    main()
    print("This is the client! The connection has been closed! Or an 'ae' has been recived")
    print("Resetting the network socket...")
    print("...Done!")
