import socket, os, time, subprocess, requests, sys, mouse, random, pygame, pyautogui, string, requests
from getpass import getpass
from zlib import decompress
from threading import Thread
host = ""

# Keyboard Driver
from pynput.keyboard import Key , Listener , Controller
keyboard = Controller()
mods = []
inputrunning = 0
def on_press(key):
    global inputexit
    if inputexit == 1:
        return False
    global host
    keystr = ""
    if key == Key.delete:
        keystr = "del"
    print(key)
    try:
        keystr = key.char
    except AttributeError:
        ae = 0
    ae = 0
    global mods
    if key == Key.ctrl_l or key == Key.ctrl_r:
        if "ctrl" not in mods:
            mods.append("ctrl")
            print("Control Held")
            ae = 1
    if key == Key.alt_l or key == Key.alt_r or key == Key.alt_gr:
        if "alt" not in mods:
            mods.append("alt")
            print("Alt Held")
            ae = 1
    if key == Key.shift:
        #if "shift" not in mods:
            #mods.append("shift")
            #print("Shift Held")
        ae = 1
    if ae == 0:
        if key == Key.ctrl_l or key == Key.ctrl_r:
            if "ctrl" in mods:
                mods.remove("ctrl")
                print("Control Released")
        if key == Key.alt_l or key == Key.alt_r:
            if "alt" in mods:
                mods.remove("alt")
                print("Alt Released")
        if key == Key.shift:
            if "shift" in mods:
                mods.remove("shift")
                print("Shift Released")

    if keystr != "":
        print("Sending key: "+str(keystr))
        thestring = host+"/keyboard?"
        if mods == []:
            thestring = thestring + "n"
        else:
            for i in range(len(mods)):
                thestring = thestring + str(mods[i])
                print("i: " + str(i))
                print(mods[i])
                if i != len(mods) - 1:
                    thestring = thestring + "&"
        thestring = thestring + "?" + str(keystr)
        print(thestring)
        requests.get(thestring)


def on_release(key):
    #print(key)
    global inputexit
    if inputexit == 1:
        return False
    ae = 0




try:
    computername = os.environ['COMPUTERNAME']
except:
    computername = "IRC_PRGM_" + str(random.randint(0,100))
firsttime = 1
WIDTH = 0
HEIGHT = 0
hei, wid = pyautogui.size()


inputexit = 0


def recvall(conn, length):
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf



def kpress(key):
    print(f"key down: {key}")
def kreles(key):
    print(f"key up: {key}")

def inputmousethread(host,port):
    try:
        time.sleep(4) # let da server startu
        print("Mouse Connected!")
        global HEIGHT
        global WIDTH
        oldstring = ""
        global event
        global inputexit
        keylist = []
        buffer = []
        allowed = string.ascii_letters
        while 1==1:
            if inputexit == 1:
                print("Disconnecting Mouse...")
                raise Exception
            mouseclick = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            eventae=pygame.event.poll()
            mousepos = pygame.mouse.get_pos()
            #print("got mouse pos")
            #print(buffer)
            if pygame.mouse.get_pressed()[0]:
                #print("click 0!")
                mouseclick = 1
            if pygame.mouse.get_pressed() [1]:
                #print("click 1!")
                mouseclick = 2
            if pygame.mouse.get_pressed() [2]:
                #print("click 3!")
                mouseclick = 3
            #print("clicks determined")
            w, h = pygame.display.get_surface().get_size()
            #print("got surface")
            # scale the mouse position window pixal size to server resolution size
            ratio_x = (HEIGHT / w) # mouse import is also revesred. This works perfectly
            ratio_y = (WIDTH / h) # mouse import is also revesred. This works perfectly
            #print("ratio: ",(ratio_x,ratio_y))
            scaledmouse = (mousepos[0] * ratio_x, mousepos[1] * ratio_y)
            #print("scaledmouse: ",scaledmouse)
            inputstring = f"{int(scaledmouse[0])}|eilo|{int(scaledmouse[1])}|eilo|{mouseclick}".encode('utf-8')
            inputmouse = [int(scaledmouse[0]), int(scaledmouse[1]), f"{mouseclick}".encode('utf-8')] # inp list
            #print("got input string... sending!")
            #print(inputstring)
            if inputstring != oldstring:
                #mouseinput(inputmouse)
                oldstring = inputstring
    except:
        print("Mouse Disconnected")


def inputkeythread(host,port):
    time.sleep(2.3) # let da server startu
    print("Keyboard Connected!")
    global HEIGHT
    global WIDTH
    global inputexit
    global inputrunning
    oldstring = ""
    #global event
    keylist = []
    buffer = []
    allowed = string.ascii_letters
    #while True:
    #    if inputexit == 1:
    #        print("Shuting down input...")
    #        raise Exception
    #    if inputrunning == 1:
    with Listener(on_press=on_press , on_release=on_release) as listener:
        listener.join()
        while True:
            time.sleep(1)
            if inputexit == 1:
                try:
                    listener.stop()
                    print("Keyboard Disconnected")
                    break
                except:
                    try:
                        Listener.stop()
                    except:
                        print("Couldnt disconnect keyboard")


# IRC Video
def ircvideo(sock):
    global WIDTH
    global HEIGHT
    global wid
    global hei
    global inputexit
    global inputrunning
    print("IRC Version 1.0")
    print("To end your IRC session, Simply close the window.")
    try:
        #print("ae")
        pygame.init()
        screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        clock = pygame.time.Clock()
        inputrunning = 0
        inputexit = 0
        watching = True    
        while watching:
            # send a single byte
            sock.send(b'\x00')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
            if inputrunning == 0:
                # start the input thread
                print("Initalizing the Input...")
                mousethread = Thread(target=inputmousethread, args=(host,port,))
                mousethread.start()
                keythread = Thread(target=inputkeythread, args=(host,port,))
                keythread.start()
                inputrunning = 1
            size_len = int.from_bytes(sock.recv(1), byteorder='big')
            size = int.from_bytes(sock.recv(size_len), byteorder='big')
            pixels = decompress(recvall(sock, size))
            img = pygame.image.fromstring(pixels, (HEIGHT, WIDTH), 'RGB')
            w, h = pygame.display.get_surface().get_size()
            DEFAULT_IMAGE_SIZE = (w,h) # these are inverted.
            img = pygame.transform.scale(img, DEFAULT_IMAGE_SIZE)
            # display it 
            screen.blit(img, (0, 0))
            pygame.display.flip()
            #pygame.display.update()
            clock.tick(60)
    finally:
        #sock.close()
        print("Please wait, Closing IRC")
        print("Disconnecting Input.")
        #Listener.stop() # stop keyboard
        sock.send("end".encode('utf-8'))
        inputexit = 1
        print("Press any key to return to the terminal")
        time.sleep(1)
        pygame.quit()
        


name = os.name
def clearscreen():
    global name
    if name == "nt":
        os.system("cls")
    else:
        os.system("clear")
clearscreen()

aemode = 0
aeip = ""
aeport = 0
port = 0

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
while True:
    print("EiLO3 HTTP Server IP Address (or URL) followed by port (:port)\n e.g. http://10.0.0.150:8080\n e.g. http://myeilo.computer.com:8080")    
    if ae != "ae":
        print(f"or press enter to use the previous session:\n{ae}")
        url = str(input("\n> "))
        if url == "ae":
            break
        if url == "":
            break
        if url.startswith("http") != 1:
            clearscreen()
            print("Thats not a URL! Use http://")
        else:
            break
    else:
        url = str(input("\n> "))
        if url == "ae":
            break
        if url.startswith("http") != 1:
            clearscreen()
            print("Thats not a URL! Use http://")
        else:
            break
if url != "":

    if url != "ae":
        with open("irc.conf","w") as f:
            ae = [url]
            f.writelines(ae)
            f.close()
    else:
        # ae special ae prompt
        clearscreen()
        while True:
            aemode = 1
            ae = input("ae!> ")
            if ae.startswith("conn ") or ae.startswith("conn"):
                try:
                    ae = ae.split("conn ")
                    ae = ae[1]
                    ae = ae.split(" ")
                    aeip = ae[0]
                    aeport = ae[1]
                    break
                except:
                    print("conn <ipaddr> <port>")
            if ae == "ae":
                print("ae version 1.0\nThe ultimate ccli for your snek")

if url == "":
    url = ae
if aemode == 0:
    host = url
    print(f"Connecting to: {url}")
    x = requests.get(f"{url}/remo")
    port = int(x.text)
    if url.startswith("http://"):
        ae = url.split("http://")
        ae = ae[1]
        ae = ae.split(":")
        ipaddr = ae[0]
if aemode == 1:
    print("\n***ae mode active***\n")
    port = aeport
    ipaddr = aeip


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
            print("Ready! INIT Remote Terminal")
            time.sleep(1)
            clearscreen()
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
                    clearscreen()
                if fromserver[2] == "exit":
                    print(fromserver[1])
                    time.sleep(0.5)
                    print("[==REMOTE SERVER CLOSED CONNECTION==]\n\n")
                    time.sleep(3)
                    ae = input("Press enter to exit")
                    client_socket.close()
                    exit()
                    sys.exit()
                    raise Exception

            except:
                ae = 0 # Do nothing
            if fromserver[0] == "NONEPASS":
                # No prompt, input showing message
                fromclient = str(getpass(f"{fromserver[1]}"))
            elif fromserver[0] == "NONE":
                # No prompt, input showing message
                fromclient = str(input(f"{fromserver[1]}"))
            # IRC Driver
            elif fromserver[0] == "IRCDRIVER":
                # We gonna start an IRC
                thestring = fromserver[1]
                thestring = thestring.split(",")
                global WIDTH
                global HEIGHT
                WIDTH = int(thestring[0])
                HEIGHT = int(thestring[1])
                print("IRC: Ready!")
                ircvideo(client_socket)
                fromclient = "end"

                time.sleep(5)

                



            else:
                # Server gives a CLI Prompt.
                print(fromserver[1]) # show message in terminal
                print("")
                fromclient = str(input(f"{fromserver[0]}"))
                if fromclient == "exit":
                    print("[==REMOTE SERVER CLOSED CONNECTION==]\n\n")
                    time.sleep(3)
                    ae = input("Press enter to exit")
                    client_socket.close()
                    exit()
                    sys.exit()
                    raise Exception
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
