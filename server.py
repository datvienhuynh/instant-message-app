# COMP3331 - COMPUTER NETWORK AND APPLICATION
# ASSIGNMENT
# Written by Vien Dat Huynh (z5223470)
# Tutor by Nipuna Shanthidewa
# Tested on Python 3

from socket import *
import socket
import sys
import threading
import time
from multiprocessing import Process
import datetime as dt
import actions

class ClientHandler(threading.Thread):

    def __init__(self, _socket, _auth_list, _address):
        threading.Thread.__init__(self)
        self.socket = _socket
        self.auth_list = _auth_list
        self.address = _address
        self.username = ''
        self.no_failed_login = 0
        self.last_active = time.time()

    # receive a user request
    def receive(self):
        input_line = self.socket.recv(2048)
        return input_line.decode()

    # send a message to the user
    def send(self, message):
        self.socket.send(message.encode())

    # give notification about a user to other users who do not block him
    def notify(self, message):
        message = actions.NOTIFY + " " + message
        for user in online_users:
            if user == self.username:
                continue
            if user in blacklist:
                if self.username in blacklist[user]:
                    continue
            online_users[user].send(message.encode())

    # deliver message to a user
    def message(self, user, message):
        message = actions.MESSAGE + " " + self.username + " " + message
        online_users[user].send(message.encode())

    # broadcast message from a user to other users who do not block him
    def broadcast(self, message):
        global online_users
        message = actions.MESSAGE + " " + self.username + " " + message
        sendall = True
        for user in online_users:
            if user == self.username:
                continue
            if user in blacklist:
                if self.username in blacklist[user]:
                    sendall = False
                    continue
            online_users[user].send(message.encode())
        if sendall == False:
            msg = actions.NOTIFY + " " + "--- Your message could not be delivered to some recipients ---"
            self.send(msg)

    # response 'whoelse' request
    def send_online_list(self):
        message = actions.NOTIFY + " Online Users:\n"
        for user in online_users:
            if user != self.username:
                message += ">> {}\n".format(user)
        self.send(message)

    # response 'whoelsesince' request
    def send_login_since(self, since):
        message = actions.NOTIFY + " Logged In Users within {} seconds:\n".format(since)
        for user in user_login_time:
            period = time.time() - user_login_time[user]
            if period <= since:
                message += ">> {}\n".format(user)
        self.send(message)

    # store an online username, socket and address in global variables
    def add_online_user(self):
        global online_users
        online_users[self.username] = self.socket
        user_address[self.username] = self.address
        self.notify(">> %s is online" % self.username)

    # send offline messages to a user who just logged in
    def check_off_messages(self):
        global offline_messages
        if self.username in offline_messages:
            for msg in offline_messages[self.username]:
                self.socket.send(msg.encode())
                time.sleep(0.1)
            offline_messages.pop(self.username)

    # authenticate a user login
    def authenticate(self):

        global online_users
        global blocked_users
        global user_login_time

        start = time.time()
        end = time.time()
        login_succeeds = False
        while login_succeeds == False:
            self.send(actions.USERNAME_INPUT)
            username = self.receive()
            self.send(actions.PASSWORD_INPUT)
            password = self.receive()
            if username in blocked_users:
                end = time.time()
                if (end - start) <= blockDuration:
                    self.send(actions.BLOCKED_ALERT)
                    time.sleep(0.1)
                    continue
                blocked_users.remove(username)
                self.no_failed_login = 0
            if username not in auth_list:
                self.send(actions.LOGIN_FAIL)
                self.no_failed_login = 0
            elif self.auth_list[username] != password:
                self.send(actions.LOGIN_FAIL)
                self.no_failed_login += 1
            elif username in online_users:
                self.send(actions.ERROR_LOGIN_ON_USER)
                self.no_failed_login = 0
            else:
                login_succeeds = True
                self.username = username
                self.no_failed_login = 0
                user_login_time[username] = time.time()
                self.send(actions.LOGIN_SUCCESS)
                self.add_online_user()
                self.last_active = time.time()
            if self.no_failed_login == 3:
                time.sleep(0.1)
                self.send(actions.BLOCKED_ALERT)
                blocked_users.append(username)
                start = time.time()
            time.sleep(0.1)

    # update all data and notify other users when someone logged out
    def logout(self):
        global online_users
        global user_address
        online_users.pop(self.username)
        user_address.pop(self.username)
        self.notify(">> {} is offline.".format(self.username))
        self.send(actions.NOTIFY + " Successfully Logged Out.")
        self.username = ''
        self.no_failed_login = 0
        time.sleep(0.1)

    # execute actions requested from users
    def take_action(self, actions_array):

        global offline_messages
        global blacklist

        if actions_array[0] == "broadcast":
            self.broadcast(actions_array[1])
        elif actions_array[0] == "message" and len(actions_array) == 2:
            data = actions_array[1].split(' ', 1)
            if data[0] not in auth_list or data[0] == self.username:
                self.send(actions.ERROR_INVALID_USER)
            elif data[0] in blacklist and self.username in blacklist[data[0]]:
                self.send(actions.NOTIFY + " >> Message cannot be sent to " + data[0])
            elif data[0] not in online_users:
                message = actions.MESSAGE + " " + self.username + " " + data[1] + "\n"
                if data[0] in offline_messages:
                    offline_messages[data[0]].append(message)
                else:
                    offline_messages[data[0]] = []
                    offline_messages[data[0]].append(message)
            elif len(data) < 2:
                self.send(actions.ERROR_COMMAND)
            else:
                self.message(data[0], data[1])
        elif actions_array[0] == "whoelse" and len(actions_array) < 2:
            self.send_online_list()
        elif actions_array[0] == "whoelsesince" and len(actions_array) == 2 and actions_array[1].isdigit():
            self.send_login_since(int(actions_array[1]))
        elif actions_array[0] == "block" and len(actions_array) == 2:
            if actions_array[1] not in auth_list:
                self.send(actions.ERROR_INVALID_USER)
            elif actions_array[1] == self.username:
                self.send(actions.NOTIFY + " >> You cannot block yourself.")
            elif self.username in blacklist:
                blacklist[self.username].append(actions_array[1])
                self.send(actions.NOTIFY + " >> " + actions_array[1] + " is added to blacklist.")
            else:
                blacklist[self.username] = []
                blacklist[self.username].append(actions_array[1])
                self.send(actions.NOTIFY + " >> " + actions_array[1] + " is added to blacklist.")
        elif actions_array[0] == "unblock" and len(actions_array) == 2:
            if actions_array[1] not in auth_list:
                self.send(actions.ERROR_INVALID_USER)
            elif actions_array[1] == self.username:
                self.send(actions.NOTIFY + " >> You cannot unblock yourself.")
            elif self.username not in blacklist or actions_array[1] not in blacklist[self.username]:
                self.send(actions.NOTIFY + " >> " + actions_array[1] + " is not in your blacklist.")
            else:
                blacklist[self.username].remove(actions_array[1])
                self.send(actions.NOTIFY + " >> " + actions_array[1] + " is unblocked from blacklist.")
        elif actions_array[0] == "startprivate":
            if actions_array[1] not in auth_list:
                self.send(actions.ERROR_INVALID_USER)
            elif actions_array[1] == self.username:
                self.send(actions.NOTIFY + " >> You cannot establish a connection with yourself")
            elif actions_array[1] in blacklist and self.username in blacklist[actions_array[1]]:
                self.send(actions.NOTIFY + " >> Cannot establish a private connection with " + actions_array[1])
            elif actions_array[1] not in online_users:
                self.send(actions.NOTIFY + " >> {} is not online".format(actions_array[1]))
            else:
                host = (user_address[actions_array[1]])[0]
                port = (user_address[actions_array[1]])[1]
                message = actions.USER_IP_PORT + " " + self.username + " " + actions_array[1] + " " + host + " " + str(port)
                self.send(message)
        elif actions_array[0] == "logout" and len(actions_array) < 2:
            self.logout()
            self.run()
        else:
            self.send(actions.ERROR_COMMAND)

    # start a new thread handling a user connection
    def run(self):
        self.authenticate()
        self.check_off_messages()

        while True:
            action_names = self.receive()
            # check the timeout
            if time.time() - self.last_active >= timeout:
                self.logout()
                self.run()
                continue
            self.last_active = time.time()
            if action_names == '' or action_names == '\n':
                continue
            actions_array = action_names.split(' ', 1)
            if len(actions_array) < 2:
                actions_array = action_names.split()
            elif len(actions_array) == 2:
                actions_array[1] = (actions_array[1].split("\n", 1))[0]
            self.take_action(actions_array)


# check if user input correct command 
if len(sys.argv) != 4:
    print("Usage: python3 server.py server_port block_duration timeout")
    exit(1)
elif sys.argv[1].isdigit() == False or sys.argv[2].isdigit() == False or sys.argv[3].isdigit() == False:
    print("server_port, block_duration and timeout must be integers")
    exit(1)
else:
    serverPort = int(sys.argv[1])
    blockDuration = int(sys.argv[2])
    timeout = int(sys.argv[3])

# (username : socket)
online_users = {}
# (username : address)
user_address = {}
# (username : [message])
offline_messages = {}
# (username : time)
user_login_time = {}
# [username]
blocked_users = []
# (username : password)
auth_list = {}
# (username : [blocked username])
blacklist = {}

# read and store usernames and passwords from credentials.txt
f = open("credentials.txt", "r")
fl = f.readlines()
for line in fl:
    data = line.split()
    auth_list[data[0]] = data[1]
    print(data[0], ': ', data[1])
f.close()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(10)

while True:
    clientSocket, address = serverSocket.accept()
    client_thread = ClientHandler(clientSocket, auth_list, address)
    client_thread.start()
