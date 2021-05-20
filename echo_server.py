#!/usr/bin/env python3

import socket
import threading
import struct

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 3000        # Port to listen on (non-privileged ports are > 1023)

# mapeaza un id de un socket
# sockets[id] = conn
sockets = {}

# mapeaza un socket de un id
# sockets_ids[conn] = id
sockets_ids = {}


currentId = 0

def session(conn, adr):
    connectionID = sockets_ids[conn]
    while True:
        try:
            data = conn.recv(1024) #primeste date in maxim 1024 de bytes
            print(data)

            packetType = struct.unpack( '!b', data[0:1] )[0]
            if packetType == 5:
                # packet : 7 + id(byte) + x(float) + y(float)
                # float = 4bytes
                packetId, x, y = struct.unpack('!bff', data)
                for s in sockets.values():
                    if s != conn:
                        send_pos_for_ID(s, connectionID, x, y)
            if packetType == 8:
                for s in sockets.values():
                    if s != conn:
                        send_color_for_specifficID(s, connectionID)
                


        except:
            print("error on socket")
            sockID = sockets_ids[conn] 
            sockets.pop(sockID)
            sockets_ids.pop(conn)
            print("Player quit: " + str(sockID))
            for s in sockets.values():
                if s != conn:
                    #print("SENDING STUFF for sock " + strsockID)
                    send_status_for_specifficID(s, sockID)
            return
        #print(data)
        #conn.sendall(data) # trimite toti bytes

def send_connected_message(sock, connected_id):
    messageType = struct.pack('!b',6)
    ID_part = struct.pack('!b', connected_id)
    try: 
        sock.sendall(messageType + ID_part )
    except:
        return

def send_pos_for_ID(sock, ID, posx, posy):
    messageType = struct.pack('!b',7)
    xbytes = struct.pack('!f', posx)
    ybytes = struct.pack('!f', posy)
    IDbytes = struct.pack('!b', ID)
    
    sock.sendall(messageType + IDbytes + xbytes + ybytes)

def send_color_for_specifficID(sock, ID):
    messageType = struct.pack('!b',9)
    IDbytes = struct.pack('!b', ID)
    
    sock.sendall(messageType + IDbytes)

def send_status_for_specifficID(sock, ID):
    messageType = struct.pack('!b',10)
    IDbytes = struct.pack('!b', ID)
    
    try:
        sock.sendall(messageType + IDbytes)
    except:
        print("Error sending on sendStatusForSpecificId!")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen() # asculta conexiuni pe portul respectiv
    while True:
        conn, addr = s.accept() # acceptarea conexiunii
        print('Connected by', addr)

        print("S-a conectat un jucator, si a primit id " + str(currentId))

        for curr_socket in sockets.values(): # anunta toti ceilalti useri ca cineva s-a conectat
            send_connected_message(curr_socket, currentId)
        
        # sockets = {1: conn_1, 2: conn_2, 3: conn_3}
        # sockets.keys() = [1,2,3] / id-urile jucatorilor deja conectati
        for curr_socket_id in sockets.keys():
            # trimite jucatorului nou-conectat, id-urile tuturor oamenilor
            # conectati pana atunci.
            send_connected_message(conn, curr_socket_id)

        sockets[currentId] = conn
        sockets_ids[conn] = currentId

        currentId += 1
        sessionThread = threading.Thread(target=session, args=(conn,addr))
        sessionThread.start()
        