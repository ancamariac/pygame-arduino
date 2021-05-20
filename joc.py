import pygame
import socket
import struct
import sys
import threading
import time

run_me = True

(width, height) = (600, 400)
screen = pygame.display.set_mode((width, height))
pygame.display.flip()
size = width, height = (32, 32)
empty_surface = pygame.Surface(size)
posx = 300
posy = 200
black = (0,0,0)


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 3000        # The port used by the server

connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connectionSocket.connect((HOST, PORT))

def send_position_packet(x: float, y: float):
    messageType = struct.pack('!b',5)
    xbytes = struct.pack('!f', x)
    ybytes = struct.pack('!f', y)
    
    connectionSocket.sendall(messageType + xbytes + ybytes)



killSwitch = False # set this to true to kill thread

def session():
    print("test")
    connectionSocket.setblocking(True)
    while True:
        if killSwitch:
            break
        data = connectionSocket.recv(1024) #primeste date in maxim 1024 de bytes
        #print(data)


        packetType = struct.unpack( '!b', data[0:1] )[0]
        if packetType == 6:
            # packet : 6 + id(byte)
            connectedId = struct.unpack( '!b', data[1:2])[0]
            others[connectedId] = (300,200)
            print ("S-a conectat un jucator cu id " + str(connectedId))
        if packetType == 7:
            # packet : 7 + id(byte) + x(float) + y(float)
            # float = 4bytes

            userId, x, y = struct.unpack('!bff', data[1:10])
            others[userId] = (x,y)

print("TEST")

sessionThread = threading.Thread(target=session, args=())
sessionThread.start()

others = {}

while run_me:
    
    screen.fill(black)
    pygame.draw.circle(screen, pygame.Color(255,0,0), (posx, posy), 10)

    for o in others.values():
        pygame.draw.circle(screen, pygame.Color(0,0,255), o, 10)

    moved = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_me = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moved = True
                posx = posx - 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                moved = True
                posx = posx + 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                moved = True
                posy = posy + 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                moved = True
                posy = posy - 10
        
    if moved:
        send_position_packet(posx,posy)
    pygame.display.flip()
pygame.quit()

connectionSocket.close()
killSwitch = True
sessionThread.join() # optional