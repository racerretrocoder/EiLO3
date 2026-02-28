# Phoenix
# Copyright (c) 2025 - 2026 Backdoor Interactive!

from socket import socket
import time, keyboard
from threading import Thread
from zlib import decompress

import pygame,pyautogui,string


WIDTH = 0
HEIGHT = 0


hei, wid = pyautogui.size()



def recvall(conn, length):
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def inputthread(host,port):
    time.sleep(4) # let da server startup xd
    port = port + 2
    sock = socket()
    sock.connect((host, port))
    print("Input Socket Connected!!")
    global HEIGHT
    global WIDTH
    oldstring = ""
    global event
    keylist = []
    buffer = []
    allowed = string.ascii_letters
    while 1==1:
        mouseclick = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        eventae=pygame.event.poll()
        mousepos = pygame.mouse.get_pos()
        #print("got mouse pos")
        print(buffer)


        if pygame.mouse.get_pressed()[0]:
            print("click 0!")
            mouseclick = 1
        if pygame.mouse.get_pressed() [1]:
            print("click 1!")
            mouseclick = 2
        if pygame.mouse.get_pressed() [2]:
            print("click 3!")
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
        #print("got input string... sending!")
        time.sleep(0)
        #print(inputstring)
        if inputstring != oldstring:
            sock.send(inputstring) # deliver inputs
            oldstring = inputstring



def mainae(host='127.0.0.1', port=5000):

    global WIDTH
    global HEIGHT
    global wid
    global hei

    sock = socket()
    sock.connect((host, port))
    print("ae!")
    #thestring = ae.decode('utf-8')
    #array = thestring.split(',')
    #WIDTH = array[0]
    #HEIGHT = array[1]
    #time.sleep(100)
    #print([WIDTH,HEIGHT])
    try:
        #print("ae")
        pygame.init()
        screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        clock = pygame.time.Clock()
        running = 0
        watching = True    
        while watching:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    watching = False
                    break
            if running == 0:
                # star the thread
                thread = Thread(target=inputthread, args=(host,port,))
                thread.start()
                running = 1
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
        sock.close()

host = "192.168.0.143"
port = 5000
print("Communicating with server...")
sockae = socket()
sockae.connect((host, port))
ae = sockae.recv(1024)
ae = ae.decode('utf-8')
ae = ae.split(",")
WIDTH = int(ae[0])
HEIGHT = int(ae[1])
print(WIDTH)
print(HEIGHT)
sockae.close()
mainae(host,port)
