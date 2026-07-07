import socket, os, time, subprocess, requests, sys, mouse, random, pygame, pyautogui, string, requests, cv2, pickle, struct
import numpy as np
from getpass import getpass
from zlib import decompress
from threading import Thread
host = ""

mousecaptured = 1

# Keyboard Driver
from pynput.keyboard import Key , Listener , Controller
keyboard = Controller()
mods = []
inputrunning = 0
screenmode = 0
class keys:
    KEY_UP = Key.up
    KEY_DOWN = Key.down
    KEY_LEFT = Key.left
    KEY_RIGHT = Key.right
    #'a': KEY_A, 'b': KEY_B, 
    keymaps = {
        Key.f1 : 'f1',
        Key.f2 : 'f2',
        Key.f3 : 'f3',
        Key.f4 : 'f4',
        Key.f5 : 'f5',
        Key.f6 : 'f6',
        Key.f7 : 'f7',
        Key.f8 : 'f8',
        Key.f9 : 'f9',
        Key.f10 : 'f1',
        Key.f11 : 'f12',
        Key.f12 : 'f12',
        Key.delete: 'del',
        Key.enter: 'enter',   
        Key.space: 'space', 
        Key.backspace: 'backspace',
        Key.esc: 'esc',
        Key.up: 'up',
        Key.down: 'dn',
        Key.left: 'lt',
        Key.right: 'rt',
        Key.tab: 'tab',
    }



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
        try:
            keystr = keys.keymaps[key]
        except:
            print("Keymaps didnt work")

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
        global host
        thestring = host + "/keyboard?"
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

inputexit = 0

keytest = 0
if keytest == 1:
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





try:
    computername = os.environ['COMPUTERNAME']
except:
    computername = "IRC_PRGM_" + str(random.randint(0,100))
firsttime = 1
WIDTH = 0
HEIGHT = 0
hei, wid = pyautogui.size()




def recv_all(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            return None
        data += packet
    return data




def kpress(key):
    print(f"key down: {key}")
def kreles(key):
    print(f"key up: {key}")


def inputmousethread(hostae,port):
    try:
        time.sleep(4) # let da server startup
        print("Mouse Connected!")
        global HEIGHT
        global WIDTH
        global mousecaptured
        oldstring = ""
        global event
        global inputexit
        global host
        keylist = []
        buffer = []
        allowed = string.ascii_letters
        xlast = 0
        ylast = 0
        xmouse = 0
        ymouse = 0
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
            xmouse = scaledmouse[0]
            ymouse = scaledmouse[1]
            if mousecaptured == 1:
                # mouse is controling
                # get distance
                if xlast == xmouse:
                    xdist = 0
                if ylast == ymouse:
                    ydist = 0
                if xlast < xmouse:
                    # mouse inc in x axis
                    xdist = xmouse - xlast
                    xlast = xmouse
                if xlast > xmouse:
                    # mouse dec in x axis
                    xdist = xlast - xmouse
                    xlast = xmouse
                    xdist = xdist * -1
                if ylast < ymouse:
                    # mouse inc in y axis
                    ydist = ymouse - ylast
                    ylast = ymouse
                if ylast > ymouse:
                    # mouse dec in y axis
                    ydist = ylast - ymouse
                    #ydist = ydist
                    ylast = ymouse
                    ydist = ydist * -1

                #print("xdist")
                #print(xdist)
                #print("ydist")
                #print(ydist)
                xlast = xmouse
                ylast = ymouse
            #print("scaledmouse: ",scaledmouse)
            inputstring = f"/mouse?{int(xdist)}&{int(ydist)}"
            if inputstring != oldstring:
                #mouseinput(inputmouse)
                oldstring = inputstring
                # send le mouse control
            try:
                requests.get(f"{host}{inputstring}")
            except:
                ae = 0
    except Exception as eee:
        print("Mouse Disconnected")
        print(str(eee))


def inputkeythread(hostae,port):
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
                    print("Keyboard Disconnected!")
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
        pygame.display.set_caption("EiLO3 Integrated Remote Console")
        inputrunning = 0
        inputexit = 0
        watching = True    
        data = b""
        payload_size = struct.calcsize("L")
        oldw = 640
        oldh = 480
        while watching:
            # send a single byte
            sock.send(b'\x00')
            width = sock.recv(4)
            height = sock.recv(4)
            #print(str(width))
            #print(str(height))
            height = int(height)
            width = int(width)
            if oldw != width:
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                oldw = width
                oldh = height
                print("Force resized the window")
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
                    #print("getting size len")
                    #size_len = int.from_bytes(sock.recv(1), byteorder='big')
                    #print(size_len)
                    #print("getting pixels")
                    #size = int.from_bytes(sock.recv(size_len), byteorder='big')
                    #print(size)
                    #print("Decompressing...")
                    #pixels = decompress(recvall(sock, size))
                    #print("Decompressed!")
                    #frame_rgb = cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB)
                    #frame_transposed = cv2.transpose(frame_rgb)
                    #img = pygame.image.fromstring(pixels, (HEIGHT, WIDTH), 'RGB')
                        #while len(data) < payload_size:
                        #    packet = sock.recv(4096)
                        #    if not packet: sys.exit()
                        #    data += packet
                        #packed_msg_size = data[:payload_size]
                        #data = data[payload_size:]
                        #msg_size = struct.unpack("L", packed_msg_size)[0]
                        #while len(data) < msg_size:
                        #    data += sock.recv(4096)
                        #frame_data = data[:msg_size]
                        #data = data[msg_size:]
                        #frame = pickle.loads(frame_data)
                        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        ##frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                        #frame_surface = pygame.surfarray.make_surface(frame)
            header = recv_all(sock, 4)
            if header:
                image_size = struct.unpack("!I", header)[0]
                #print(f"Expecting image payload of {str(image_size)} bytes...")
            image_bytes = recv_all(sock, image_size)
            RESOLUTION = (width, height)
            if image_bytes:
                #print("Image transmission appearntly complete")
                image_bytes = decompress(image_bytes)
                try:
                    img = pygame.image.frombytes(image_bytes, RESOLUTION, "RGB")
                except:
                    img = pygame.image.fromstring(image_bytes, RESOLUTION, "RGB")
            w, h = pygame.display.get_surface().get_size()
            DEFAULT_IMAGE_SIZE = (w,h) # these are inverted.
            img = pygame.transform.scale(img, DEFAULT_IMAGE_SIZE)
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(60)
    except Exception as ae:
        print("Please wait, Closing IRC err: " + str(ae))
        print("Disconnecting Input.")
        sock.send("end".encode('utf-8'))
        inputexit = 1
        print("Press any key to return to the terminal")
        time.sleep(1)
        pygame.quit()
        inputexit = 1
        inputrunning = 0
        


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
                client_socket.send(fromclient.encode('utf-8'))
                time.sleep(5)
                print("IRC: Quit")
                pygame.quit()

                



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
