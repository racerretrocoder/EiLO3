# Phoenix
# Copyright (c) 2025 - 2026 Backdoor Interactive!
from socket import socket
import socket as socketae
from threading import Thread
from zlib import compress
import pyautogui, time, ctypes, mouse, keyboard
from mss import mss

screen_size_x, screen_size_y = pyautogui.size()
WIDTH = screen_size_y
HEIGHT = screen_size_x

oldmousex = 0
oldmousey = 0
oldclick = 0

def inputae():
    global oldmousex
    global oldmousey
    global oldclick
    port = 5000
    port = port + 2
    print("Input!")
    sockinput = socketae.socket(socketae.AF_INET, socketae.SOCK_STREAM)
    host = "0.0.0.0"
    sockinput.bind((host, port))
    sockinput.listen(5)
    conn, addr = sockinput.accept()
    while True:
        msg = conn.recv(1024) # Input stuff
        input = msg.decode('utf-8')
        inputarray = input.split('|eilo|')
        #print(input)
        mousex = inputarray[0]
        mousey = inputarray[1]
        #print("Mouse in Client: ",(mousex,mousey))
        mouseclick = int(inputarray[2])
        #print("Click: ",mouseclick)
        #ae = mouse.get_position() 
        #current position of the mouse using the "position" function
        #position = ae
        #print("Mouseposition: ",position)
        if mousex != oldmousex or mousey != oldmousey:
            mouse.move(mousex,mousey, duration=0.1)
            oldmousex = mousex
            oldmousey = mousey
        if mouseclick != oldclick:
            # clik
            print("click")
            if mouseclick == 1:
                mouse.click("left")
                oldclick = mouseclick
            if mouseclick == 3:
                mouse.right_click()
                oldclick = mouseclick      
            if mouseclick == 0:
                oldclick = 0



def retreive_screenshot(conn,sock): # sock is only used to close it
    global WIDTH
    global HEIGHT
 
    ctypes.windll.user32.SetProcessDPIAware(1)
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}
        try:
            running = 0
            while 1 == 1:
            # Capture the screen
                global oldmousex
                global oldmousey
                img = sct.grab(sct.monitors[1]) # rect supposed to replace sct.monitors[1]
            # Tweak the compression level here (0-9)
                pixels = compress(img.rgb, 9)

            # Send the size of the pixels length
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                conn.send(bytes([size_len]))

            # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')

                conn.send(size_bytes)

            # Send pixels
                conn.sendall(pixels)
        except:
            print("Client disconnected!")
            
            conn.close()
            sock.close()
            time.sleep(3)
            handshake()


def main(host='0.0.0.0', port=5000):

    sock = socket()
    sock.bind((host, port))
    global WIDTH
    global HEIGHT
    try:
        sock.listen(5)
        print('Server started.')

        while 'connected':
            conn, addr = sock.accept()

            print('Client connected IP:', addr)
            threadae = Thread(target=inputae, args=())
            threadae.start()
            thread = Thread(target=retreive_screenshot, args=(conn,sock,))
            thread.start()

    finally:
        print("\n\n\n\n\n\n\n")
        sock.close()
        conn.close()
        print("rest back to HS state!")
        handshake() # go back


def handshake():
    host='0.0.0.0' 
    port=5000
    inputport=port+2
    sockae = socket()
    #sockae.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sockae.bind((host, port))
    sockae.listen(5)
    print('doing screen handshake. 2')

    conn, addr = sockae.accept()
    thestring = f"{WIDTH},{HEIGHT}"
    conn.send(thestring.encode('utf-8'))
    print("sending scree")
    conn.close()
    conn.close()
    sockae.close()
    sockae.close()
    sockae = ""
    sock = ""
    conn = "" # deletion xd
    main()
handshake()
