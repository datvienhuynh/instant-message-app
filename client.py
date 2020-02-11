# COMP3331 - COMPUTER NETWORK AND APPLICATION
# ASSIGNMENT
# Written by Vien Dat Huynh (z5223470)
# Tutor by Nipuna Shanthidewa
# Tested on Python 3

from socket import *
import socket
import sys
import select
import threading
import time
import datetime as dt
import actions

class Client(threading.Thread):

    def __init__(self, _socket):
        threading.Thread.__init__(self)
        self.socket = _socket
        self.private_conn = {}
        self.username = ""

    # send a message to server
    def send(self, message):
        self.socket.send(message.encode())

    # receive a message from server
    def receive(self):
        input_line = self.socket.recv(2048)
        return input_line.decode()

    # take actions received from server
    def take_action(self, actions_array):
        input_line = ""
        if actions_array[0] == actions.USERNAME_INPUT:
            input_line = input("> Username: ")
        elif actions_array[0] == actions.PASSWORD_INPUT:
            input_line = input("> Password: ")
        elif actions_array[0] == actions.LOGIN_FAIL:
            print("--- Username or password is invalid ---")
        elif actions_array[0] == actions.BLOCKED_ALERT:
            print("--- Your account has been blocked. Please try again later ---")
        elif actions_array[0] == actions.LOGIN_SUCCESS:
            print(">>>>>>>>>>>> WELCOME TO THE MESSAGE APP!!! <<<<<<<<<<<<")
        elif actions_array[0] == actions.NOTIFY:
            print(actions_array[1])
        elif actions_array[0] == actions.MESSAGE:
            message_array = actions_array[1].split(" ", 1)
            print(message_array[0] + ": " + message_array[1])
        elif actions_array[0] == actions.ERROR_COMMAND:
            print("--- The command is invalid, please retry ---")
        elif actions_array[0] == actions.ERROR_INVALID_USER:
            print("--- The input username is invalid, please retry ---")
        elif actions_array[0] == actions.ERROR_LOGIN_ON_USER:
            print("--- This user is being online, please try another username ---")
        # if receiving username, IP address and port, create a new socket
        # to connect with another peer
        elif actions_array[0] == actions.USER_IP_PORT:
            peer_info = actions_array[1].split()
            peer_address = (peer_info[2], int(peer_info[3]))
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.connect(peer_address)
            self.private_conn[peer_info[1]] = new_socket
            self.username = peer_info[0]
            print("--- Start private messaging with %s ---" % peer_info[1])
        # print when receiving a private message
        elif actions_array[0] == "private" and len(actions_array) == 2:
            peer_info = actions_array[1].split(" ", 1)
            print(peer_info[0] + " (private): " + peer_info[1])
        else:
            input_line = input("")
        self.send(input_line)

    # handle all the actions received from user input and server
    def handle_connection(self):
        action_name = "_"
        while True:
            socket_list = [sys.stdin, clientSocket]
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
            for sock in read_sockets:
                # if it is from server
                if sock == clientSocket:
                    action_name = self.receive()
                    actions_array = action_name.split(" ", 1)
                    if len(actions_array) < 2:
                        actions_array = action_name.split()
                    self.take_action(actions_array)
                # if it is from stdin
                else :
                    message = sys.stdin.readline()
                    actions_array = message.split(' ', 1)
                    if actions_array[0] == "private" and len(actions_array) == 2:
                        message_info = actions_array[1].split(' ', 1)
                        if len(message_info) == 2 and message_info[0] in self.private_conn:
                            peer_msg = self.username + " (private): " + message_info[1]
                            self.private_conn[message_info[0]].send(peer_msg.encode())
                        elif message_info[0] not in self.private_conn:
                            print("--- Execute startprivate before sending private messages ---")
                        else:
                            print("--- The command is invalid, please retry ---")
                        continue
                    elif actions_array[0] == "stopprivate" and len(actions_array) == 2:
                        actions_array[1] = (actions_array[1].split("\n", 1))[0]
                        print(actions_array[1])
                        if actions_array[1] not in self.private_conn:
                            print("--- There is no P2P connection with %s ---" % actions_array[1]) 
                        else:
                            msg = actions.P2P_CLOSE + " " + self.username
                            self.private_conn[actions_array[1]].send(msg.encode())
                            self.private_conn[actions_array[1]].close()
                            self.private_conn.pop(actions_array[1])
                            print("--- P2P connection with %s closed ---" % actions_array[1])
                        continue
                    self.send(message)
        
        print("Connection closed")
        self.socket.close()

    # start a new socket to listen to other peers connection request
    def run(self):
        while True:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind(clientSocket.getsockname())
            listen_socket.listen(10)
            connection, peer_address = listen_socket.accept()
            new_peer_thread = self.P2PHandler(connection)
            new_peer_thread.start()

    # class handle the P2P connection
    class P2PHandler(threading.Thread):
        def __init__(self, _connection):
            threading.Thread.__init__(self)
            self.connection = _connection

        def run(self):
            while True:
                action_name = self.connection.recv(2048)
                action_name = action_name.decode()
                actions_array = action_name.split(" ", 1)
                if actions_array[0] == actions.P2P_CLOSE:
                    print("--- P2P connection with %s closed ---" % actions_array[1])
                    break
                print(action_name)

# check the command line arguments
if len(sys.argv) != 3:
    print("Usage: python3 client.py server_IP server_port")
    exit(1)
else:
    serverIP = sys.argv[1]
    serverPort = int(sys.argv[2])

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSocket.bind(('localhost', 0))
clientSocket.connect((serverIP, serverPort))

client = Client(clientSocket)
client.start()
client.handle_connection()
