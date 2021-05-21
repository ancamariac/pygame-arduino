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


HOST = '192.168.1.6'  # The server's hostname or IP address
PORT = 1000        # The port used by the server

connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connectionSocket.connect((HOST, PORT))

def send_position_packet(x: float, y: float):
    messageType = struct.pack('!b',5)
    xbytes = struct.pack('!f', x)
    ybytes = struct.pack('!f', y)
    
    connectionSocket.sendall(messageType + xbytes + ybytes)

# pachet pentru a trimite serverului intentia de a transforma culoarea
def send_color_command():
    messageType = struct.pack('!b',8)  
    connectionSocket.sendall(messageType)

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
            others_colors[connectedId] = pygame.Color(0,0,255)
            print ("S-a conectat un jucator cu id " + str(connectedId))
        if packetType == 7:
            # packet : 7 + id(byte) + x(float) + y(float)
            # float = 4bytes

            userId, x, y = struct.unpack('!bff', data[1:10]) # incepe de la 1 inclusiv - 10 exclusiv (bytes)
            others[userId] = (x,y)
        if packetType == 9:
            userId = struct.unpack('!b', data[1:2])[0]
            print("Playerul cu userid:" + str(userId) + "s-a facut alb")
            others_colors[userId] = white
        if packetType == 10:
            userId = struct.unpack('!b', data[1:2])[0]
            print(str(userId) + "a iesit din joc")
            others.pop(userId)
            others_colors.pop(userId)

print("TEST")

sessionThread = threading.Thread(target=session, args=())
sessionThread.start()

others = {}
others_colors = {}

white = pygame.Color(255,255,255)

myColor = pygame.Color(255,0,0)

while run_me:
    
    screen.fill(black)
    pygame.draw.circle(screen, myColor, (posx, posy), 10)

    for o in others.keys():
        pygame.draw.circle(screen, others_colors[o], others[o], 10)

    moved = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_me = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                send_color_command()
                myColor = white
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
                posy = posy - 10
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                moved = True
                posy = posy + 10
        
    if moved:
        send_position_packet(posx,posy)
    pygame.display.flip()
pygame.quit()

connectionSocket.close()
killSwitch = True
sessionThread.join() # optional