# Communications Implementations

## Overview
This document details how the communications between the client and the server should be implemented. When a new 
feature is added to the client or server, this document should be updated to reflect the changes. This document will not
detail how the client and server will be function internally, but rather how they will communicate with each other.  

The communications between the client and server will be implemented using json messages.

---
## Client
The client will be implemented using the python sockets library. The client will be able to connect to the server and 
send messages to the server. The client will also be able to receive messages from the server.

### Client Requests
The client will be able to send the following requests to the server:

#### Sending Messages
When sending user messages to the server it should send them with the following format:
```json
{"user":"USERNAME", "type":"message", "message":"MESSAGE GOES HERE"}
```

#### User List
When the user uses the "/users" command, it should send the following message:
```json
{"user":"USERNAME", "type":"userlist", "onlinetype":"true/false"}
```

This will request a list of users from the server to display to the user. 

If onlinetype is true, the server will send the client a list of all the users that are currently online. If onlinetype is
false, the server will send the client a list of all the users that are currently offline.

#### Guest Login
The guest login system is only for early clients and will not be used past the release of V0.2.0. The client will send
the following message to the server:
```json
{"user":"USERNAME", "type":"guest"}
```

#### Request Salt
Before the client can log in to the server, it will need to request a salt from the server. The client will send the following
message to the server:
```json
{"user":"USERNAME", "type":"salt"}
```

The server will reply with the salt associated with the username in the json file. 

#### Login Request 
When the user is joining the server, before they are connected to the chatroom they will need to log in. The client will
send the following message to the server:
```json
{"user":"USERNAME", "type":"login", "password":"PASSWORD"}
```

The server will then check the password against the salted password in the json file. If the password is correct, the
server will connect the user to the server and send a success message back. If the password is incorrect, the server will
send a failure message back and allow the user to try again a limited number of times before disconnecting them and closing
the client window.

#### Register Account
If the user does not alreadt have an account, they will need to register an account. The client will send the following
message to the server:
```json
{"user":"USERNAME", "type":"register"}
```

The server will then respond a message in the following format:
```json
{"type":"username_register_status", "taken":"true/false"}
```
If taken is true, the username is already taken and the client will display a message to the user saying that the username
is already taken and allow the user to try again. If taken is false, the username is not taken and the register process will continue.

This will create a new account in the json file with a random salt and a blank password. The client will then send the
salt back in the following message:
```json
{"type":"salt", "salt":"SALT"}
```
The client will then send the password back in the following message:
```json
{"user":"USERNAME", "type":"login", "password":"PASSWORD"}
```

#### Disconnect Request
When the user is leaving the server, they will need to disconnect from the server. The client will send the following
message to the server:
```json
{"user":"USERNAME", "type":"disconnect"}
```

#### Typing Status
When the user starts typing a message in the message box the client will send the following request to the server:
```json
{"user":"USERNAME", "type":"typing", "status":"true"}
```
When the user stops typing (either by sending the message or by deleting the message) the client will send the following
request to the server:
```json
{"user":"USERNAME", "type":"typing", "status":"false"}
```

### Client Handling
The client will be able to handle the following messages from the server:

#### Message
When the client receives a broadcasted user message from the server, it will be in this format:
```json
{"type":"message", "from":"USERNAME", "message":"MESSAGE GOES HERE"}
```

#### User List
When the client receives a user list from the server, it will be in this format:
```json
{"type": "userlist", "users": ["USER1", "USER2", "USER3"], "onlinetype": "True/False"}
```

#### Join and Leave Messages
When the client receives a join or leave message from the server, it will be in this format:
```json
{"type":"user_notification", "user":"USERNAME", "status":"true/false"}
```
These messages will be received when a user joins or leaves the server. 
If status is true, the client will display a message to the user saying that the user has joined the server.
If status is false, the client will display a message to the user saying that the user has left the server.

#### Salt
When the client receives a salt from the server, it will be in this format:
```json
{"type":"salt", "salt":"SALT"}
```

#### Client Shutdown
When the client receives a shutdown message from the server, it will be in this format:
```json
{"type":"shutdown"}
```
This message will be received when the server is shutting down. The client will then close the connection to the server
and close the client window and display a message to the user saying that the server is shutting down.

#### Outdated Client
When the client receives an outdated client message from the server, it will be in this format:
```json
{"type":"outdated_client", "version":"VERSION"}
```
This message will be received when the client is outdated and needs to be updated. The client will then close the connection
to the server and close the client window and display a message to the user saying that the client is outdated and needs to
be updated to version VERSION.

#### Guest Login Username Taken
When the client receives a guest login username taken message from the server, it will be in this format:
```json
{"type":"username_taken"}
```
This message will be received when the user is trying to log in as a guest and the username is already taken. The client
will then display a message to the user saying that the username is already taken and allow the user to try again.

#### Typing Status
When the client receives a typing status message from the server, it will be in this format:
```json
{"type":"typing", "user":"USERNAME", "status":"true/false"}
```

This message will be received when a user starts or stops typing a message. The client will then display a message to the
user saying that the user is typing a message below the message box.

#### Login Status
When the client receives a login status message from the server, it will be in this format:
```json
{"type":"login_status", "status":"true/false"}
```
"status" will be true if the login was successful and false if the login was unsuccessful. If the login was successful, the
client will connect the user to the server and allow them to send messages. If the login was unsuccessful, the client will
display a message to the user saying that the login was unsuccessful and allow the user to try again a limited number of
times before disconnecting them and closing the client window. 

#### Register Status
When the client receives a register status message from the server, it will be in this format:
```json
{"type":"register_status", "status":"true/false", "additional_info":"ADDITIONAL INFO"}
```
"status" will be true if the register was successful and false if the register was unsuccessful. If the register was
successful, the client will connect the user to the server and allow them to send messages. If the register was
unsuccessful, the client will display an error message to the user saying that the register was unsuccessful with the 
reason in "additional_info" and allow the user to try again a limited number of times before disconnecting them and closing
the client window.



---
## Server
The server will be implemented using the python sockets library. The server will be able to connect to the client and
send messages to the client. The server will also be able to receive messages from the client.

### Server Requests

#### Shutdown Request
When the server is shutting down, it will send the following message to all the clients:
```json
{"type":"shutdown"}
```

This wil allow the clients to close the connection to the server and close the client window and display a message to the
user saying that the server is shutting down.

#### User List
When the server is sending a user list to the client, it will send the following message:
```json
{"type":"userlist", "users":["USER1", "USER2", "USER3"]}
```

#### Salt
When the server is sending a salt to the client, it will send the following message:
```json
{"type":"salt", "salt":"SALT"}
```

Note: The username must not be sent with the salt for security reasons.

#### Login Success
When the server is sending a login success message to the client, it will send the following message:
```json
{"type":"login", "success":"true"}
```

#### Login Failure
When the server is sending a login failure message to the client, it will send the following message:
```json
{"type":"login", "success":"false"}
```

#### Distributing Messages
When the server receives a message from the client with type:"message" it will send the following message to all 
connected and logged in clients:
```json
{"type":"message", "from":"USERNAME", "message":"MESSAGE GOES HERE"}
```

### Server Handling
The server will be able to handle the following messages from the client:

Note: The server will only handle messages from clients that are logged in.
Note: Before the server handles any messages other than login and register requests, it will check if the ip address of the
client is in the banned list. If it is, the server will send the following message to the client:
```json
{"type":"banned"}
```
The server will then close the connection to the client.
Note: Before the server handles any messages other than login and register requests, it will check if the ip address of the
client is the correct one associated with the username. If it is not, the server will send the following message to the client:
```json
{"type":"wrong_ip"}
```
The server will then close the connection to the client.

#### Broadcasting Messages
A broadcast message will be received in the following format:
```json
{"user":"USERNAME", "type":"message", "message":"MESSAGE GOES HERE"}
```
When the server receives a message from the client with type:"message" it will send the following message to all
connected and logged in clients:
```json
{"type":"message", "from":"USERNAME", "message":"MESSAGE GOES HERE"}
```

#### User List
A user list request will be received in the following format:
```json
{"user":"USERNAME", "type":"userlist", "onlinetype":"true/false"}
```

When the server receives a user list request from the client, it will send the following message to the client:
```json
{"type":"userlist", "users":["USER1", "USER2", "USER3"], "onlinetype":"true/false"}
```
"onlinetype" will be true if the user list is of online users and false if the user list is of offline users.

#### Guest Login
A guest login request will be received in the following format:
```json
{"user":"USERNAME", "type":"guest"}
```

When the server receives a guest login request from the client, it will send the following message to the client:
```json
{"type":"login", "success":"true/false"}
```
"success" will be true if the login was successful and false if the login was unsuccessful. If the login was successful, the
server will add the user to the list of connected users and send the following message to all connected and logged in:
```json
{"type":"user_notification", "user":"USERNAME", "status":"true"}
```
If the login was unsuccessful, the server will send the following message to the client:
```json
{"type":"username_taken"}
```

#### Request Salt
A salt request will be received in the following format:
```json
{"user":"USERNAME", "type":"salt"}
```

When the server receives a salt request from the client, it will send the following message to the client:
```json
{"type":"salt", "salt":"SALT"}
```
The "salt" value will be the salt value associated with the username in the file.

#### Login
A login request will be received in the following format:
```json
{"user":"USERNAME", "type":"login", "password":"PASSWORD"}
```

When the server receives a login request from the client, it will send the following message to the client:
```json
{"type":"login", "success":"true/false"}
```

"success" will be true if the login was successful and false if the login was unsuccessful. The success of the login will be
determined by the username and password in the file. The hashed password will be compared to the hashed password in the
file. If the login was successful, the server will add the user to the list of connected users and send the following
message to all connected and logged in clients:
```json
{"type":"user_notification", "user":"USERNAME", "status":"true"}
```

If a login is successful, a temporary association will be made between the username and the ip address of the client. This
will prevent the same user from logging in from multiple locations at the same time and will prevent other users from sending
fake messages from the logged-in user. The association will be removed when the user logs out or the server is shut down.

#### Register
A register request will be received in the following format:
```json
{"user":"USERNAME", "type":"register"}
```

The server will first check if the username is already in the file. If the username is already in the file, the
server will send the following message to the client:
```json
{"type":"username_register_status", "taken":"true"}
```

If the username is not in the file the server will send the following message to the client:
```json
{"type":"username_register_status", "taken":"false"}
```

When the server receives a register request from the client, it will create a new user in the file with the username
provided by the client. The salt will be a random 32 digit integer. The password should be left blank.

The client will then send a salt request to the server using the username provided by the client in the following format:
```json
{"user":"USERNAME", "type":"salt"}
```

The server will then send the salt to the client in the following format:
```json
{"type":"salt", "salt":"SALT"}
```

The client will then send a login request to the server using the username provided by the client in the following format:
```json
{"user":"USERNAME", "type":"login", "password":"PASSWORD"}
```

The server should set the password value in the file to the hashed password provided by the client. The server will then
send the following message to the client and perform all logic associated with a successful login:
```json
{"type":"login", "success":"true"}
```

#### Disconnect Request
A disconnect request will be received in the following format:
```json
{"user":"USERNAME", "type":"disconnect"}
```

When the server receives a disconnect request from the client, it will remove the user from the list of connected users
and send the following message to all connected and logged in clients:
```json
{"type":"user_notification", "user":"USERNAME", "status":"false"}
```

