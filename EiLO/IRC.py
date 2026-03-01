import socket, os, time, subprocess, requests
computername = os.environ['COMPUTERNAME']
firsttime = 1
try:
    with open("irc.conf","r") as f:
        ae = f.read()
        #print(ae)
        ae = ae.replace("\n","")
        #print(ae)
        oldurl = ae
        f.close()
except:
    ae = "ae"


# Integrated Remote Console
print("EiLO3 Remote console\n")
print("EiLO3 HTTP Server IP Address (or URL) followed by port (:port)\n e.g. http://10.0.0.150:8080")    
if ae != "ae":
    print(f"or press enter to use the previous session:\n{ae}")
url = str(input("\n> "))
if url != "":
    with open("irc.conf","w") as f:
        ae = [url]
        f.writelines(ae)
        f.close()
if url == "":
    url = ae

print(f"Connecting to: {url}")
x = requests.get(f"{url}/remo")
port = int(x.text)
#print("Found the port ae: ",port)
if url.startswith("http://"):
    ae = url.split("http://")
    ae = ae[1]
    ae = ae.split(":")
    ipaddr = ae[0]
#port = int(input("Enter the port to connect to (The default is 5000)\nPort: "))


def client_program():
    global firsttime
    global port
    global ipaddr
    host = ipaddr # socket.gethostname()  # as both code is running on same pc
    port = int(port)  # socket server port number
    print(f"Using port: {port}")
    print(f"Connecting to {host} on {port}...")
    client_socket = socket.socket()  # instantiate
    while True: # big loop
        try:
            client_socket.connect((host, port))  # connect to the server
            print("Connected!")
            print("Retrieving Session Settings...")
            time.sleep(3)
            print("Ready! INIT Console")
            time.sleep(1)
            os.system("clear")
            os.system("cls")
            break
        except Exception as e:
            time.sleep(1) # failed to connect
            print("Failed! Trying next port.")
            port = port + 1
    msg = 'Command recived' # INIT Handshake
    message = str(f'{computername}&& {msg}\n')
    client_socket.send(message.encode())
    while message.lower().strip() != 'bye':
        firsttime = 0
        data = client_socket.recv(1024).decode()  # receive response
        if data != "Hello": # Not a heart beat message
            # parse the data
            fromserver = data.split("&&")
            # [0] is the prompt
            # [1] is the message
            # [2] is any system command
            
            # detect sys
            try:
                if fromserver[2] == "cls":
                    os.system("cls") 
                if fromserver[2] == "exit":
                    print(fromserver[1])
                    time.sleep(0.5)
                    print("[==REMOTE SERVER CLOSED CONNECTION==]\n\n")
                    time.sleep(3)
                    client_socket.close()

            except:
                ae = 0 # Do nothing
            if fromserver[0] == "NONE":
                # No prompt, input showing message
                fromclient = str(input(f"{fromserver[1]}"))
            else:
                # Server gives a CLI Prompt.
                print(fromserver[1]) # show message in terminal
                fromclient = str(input(f"{fromserver[0]}"))
            time.sleep(0.5)

        
            msgreturn = f"{computername}&&{fromclient}" # Must be different from "ae" and "Command recived"
            client_socket.send(msgreturn.encode()) # send it back             
        else:
            print("Server heartbeat! | SUCCESS")
            msgreturn = f"ae"
            client_socket.send(msgreturn.encode())

    client_socket.close()  # close the connection


if __name__ == '__main__':
    while True:
        client_program() # DA LOOP!
