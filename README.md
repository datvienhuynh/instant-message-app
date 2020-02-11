## instant-message-app
A Python application provides instant and offline messaging services based on client-server and peer-to-peer models.

The application is based on a client server model consisting of one server and multiple messaging clients. The clients communicate with the server using TCP. The server is mainly used to authenticate the clients and direct the messages (online or offline) between clients. Besides, the server also has to support certain additional functions (presence notification, blacklisting, timeout, etc.). It also implements functionality that allows clients to send peer- to-peer messages to each other that bypass the server. The application includes 2 major modules, the server program and the client program. The server program will be run first followed by multiple instances of the client program (Each instance supports one client). They will be run from the terminals on the same and/or different hosts.

# Server

The server has the following responsibilities
User Authentication - When a new client requests for a connection, the server should prompt the user to input the username and password and authenticate the user. The valid username and password combinations will be stored in a file called credentials.txt which will be in the same directory as the server program. An example credentials.txt file is provided on the assignment page. Username and passwords are case-sensitive. We may use a different file for testing so DO NOT hardcode this information in your program. You may assume that each username and password will be on a separate line and that there will be one white space between the two. If the credentials are correct, the client is considered to be logged in (i.e. online) and a welcome message is displayed. When all messaging is done, a user should be able to logout from the server.
On entering invalid credentials, the user is prompted to retry. After 3 consecutive failed attempts, the user is blocked for a duration of block_duration seconds (block_duration is a command line argument supplied to the server) and cannot login during this duration (even from another IP address). While a user is online, if someone uses the same username/password to log in (even from another IP address), then this new login attempt is denied.
Timeout - The server should keep track of all online users. If the server does not receive any commands from a user for a period of timeout seconds (timeout is a command line argument supplied to the server), then the server should automatically log this user out. Note that, to be considered active, a user must actively issue a command. The receipt of a message does not count.
Presence Broadcasts - The server should notify the presence/absence of other users logged into the server, i.e. send a broadcast notification to all online users when a user logs in and logs out.
List of online users - The server should provide a list of users that are currently online in response to such a query from a user.
Online history – The sever should provide a list of users that logged in for a user specified time in the past (e.g. users who logged in within the past 15 minutes).
Message Forwarding - The server should forward each instant message to the correct recipient assuming they are online.
Offline Messaging - When the recipient of a message is not logged in (i.e. is offline), the message will be saved by the server. When the recipient logs in next, the server will send all the unread messages stored for that user (timestamps are not required).
Message Broadcast – The server should allow a user to broadcast a message to all online users. Offline messaging is not required for broadcast messages.
Blacklisting - The server should allow a user to block / unblock any other user. For example, if user A has blocked user B, B can no longer send messages to A i.e. the server should intercept such messages and inform B that the message cannot be forwarded. Blocked users also do not get presence notifications i.e. B will not be informed each time A logs in or logs out.  

# Client

The client has the following responsibilities
Authentication - The client should provide a login prompt to enable the user to authenticate with the server.
Message - The client should allow the user to send a message to any other user and display messages sent by other users. The client should also allow the user to send a broadcast message to all online users.
Notifications - The client should display presence notifications sent by the server about users logging in and out from the server.
Find users online - The client should provide a way for the user to obtain a list of all the users currently online from the server.
Find online history – The client should provide a way for the user to obtain a list of all users who had logged in within a user specified time period.
Blacklist – The client should allow a user to block a user from sending any further messages. The client should also allow a user to unblock a user that was earlier blocked.

# Commands supported by the client

After a user is logged in, the client should support all the commands shown in the table below. 
For the following, assume that commands were run by user A.
  
message <user> <message>: Send <message> to <user> through the server. If the user is online then deliver the message immediately, else store the message for offline delivery. If <user> has blocked A, then a message to that effect should be displayed for A. If the <user> is not present in the credentials file (i.e. invalid user) or is self (A) then an appropriate error message should be displayed. The <message> used in our tests will be a few words at most.
broadcast <message>: Send <message> to all online users except A and those users who have blocked A. Inform A that message could not be sent to some recipients.
whoelse: This should display the names of all users that are currently online excluding A. Users can be displayed in any order.
whoelsesince <time>: This should display the names of all users who were logged in at any time within the past <time> seconds excluding A. Note that this, may include users that may currently be offline. If <time> is greater than the time since when the server has been running, then all users who logged in since the sever initiation time should be listed. This suggests that you will need to keep a login history since the start of the server. Users can be displayed in any order.
block <user>: blocks the <user> from sending messages to A. A message should be displayed to A confirming the blocking action. If <user> is self (i.e., A) or is invalid, then an appropriate error message should be displayed. <user> must not be informed that A has blocked them.
unblock <user>: unblocks the <user> who has been previously blocked by A. A message should be displayed to A confirming the unblocking action. If <user> is self (i.e., A) or is invalid or was not already blocked, then an appropriate error message should be displayed.
logout: log out user A.

# Peer to Peer Messaging

Some users may prefer to have some privacy during messaging. They may want to message their friends directly without all their conversation being routed via the server. A peer-to-peer messaging client is a good solution for this scenario. In addition to the above functionalities, you should implement peer-to-peer messaging (also referred to as private messaging).
To implement this functionality your client should support the following commands (in addition to those listed in Section 3.3.
startprivate <user>: This command indicates that user A wishes to commence p2p messaging with <user>. The client should obtain the IP address and port number being used by the <user> from the server. The client should try to establish a TCP connection to this IP address and port number combination. A confirmation message should be displayed to A. If <user> has blocked A, then server should not provide the IP address and port number and an appropriate error message should be displayed. If <user> is offline, invalid or self then appropriate error messages should be displayed.
private <user> <message>: Send <message> to <user> directly without routing through the server. If the user is no longer online at the address obtained via the previous command then a message to that effect should be displayed for A. If A has not executed startprivate before this command then an appropriate error message should be displayed. Note that, A may execute startprivate <user> before <user> has blocked A. In this instance, A can still use this command to send a message to <user>. Other error messages (e.g. offline, invalid, etc.) are consistent with those indicated in the above command.
stopprivate <user>: This command indicates that user A wishes to discontinue the p2p messaging session with <user>. A message to this effect should be displayed on the terminal for <user>. The TCP connection established between the two end points should be closed. An appropriate error message should be displayed if there does not exist an active p2p messaging session with <user>.


##	Application layers
#	Server
The file server.py provides a class ClientHandler which is multithreading. This class takes responsibility of handling the connection with one client. Every time a new client tries to connect to the server, a new object of this class will be created and offer a socket connecting with that client. This new object will then receive all the requests from that client, change the data and response.
Also, server.py contains seven global variables that are shared between all the objects of the class ClientHandler:
•	Online_user: A dictionary contains all the users that are logged in. The key is a username and the value is a socket that connects to the client that is using that username.
•	User_address: A dictionary contains all the addresses (IP and port) of users that are logged in. The key is a username and the value is the address of the client that is using that username. This variable helps the server to store the addresses of online users and provide them when there are requests for P2P connections.
•	Offline_messages: A dictionary contains all the messages of the offline users. The key is a username and the value is a list of all the messages. When this user logs in, this dictionary will be retrieved and send to him.
•	User_login_time: A dictionary contains all the login time of users. The key is a username and the value is an object of time. This is used for the whoelsesince requests.
•	Blocked_users: A list contains all the blocked users who has failed after logging in three times.
•	Auth_list: A dictionary contains all the user authentication read from credentials.txt. The key is a username and the value is a password.
•	Blacklist: A dictionary contains all the blacklists of users. The key is a username that has a blacklist and the value is a list containing all his blocked users.

#	Client
The file client.py implements a class Client which takes responsibility for a user connection with the server and other peers. Each object of this class contains three attributes:
•	Socket: The socket connects this client with the server.
•	Private_conn: A dictionary contains all the private P2P connections of this client. The key is the username that this user has a private connection and the value is a socket that connects to that username.
•	Username: The username of this client. Before successfully logging in, this variable is an empty string.
The class Client also offers a class P2PHandler which is multithreading. Every time another peer tries to connect with the user, an object of this class is created and accepts the connection for private messages.

##	How the system works
When the server.py is started, it reads all the user information from the credentials.txt and store in auth_list. Then it creates a new socket listening to a new connection from clients. Every time a new connection is accepted, a new threading object of ClientHandler is created and handle all the actions between this new user and the server. All of ClientHandler objects interact with each other through seven global variables listed below.
Similarly, when the client.py started, a new socket is created and connects to the given server address. Then an object of Client is generated and handle all the request and response between this new client and the server. For the P2P connections, inside an object of Client there is a multithreading object of P2PHandler which handles a socket listening to connections from other peers. When there is a new request from another user for private connection, this object will accept and receive requests from the peer. After that, a new object of P2PHandler is created and keeps listening to other peer connections.




