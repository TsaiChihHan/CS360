# CS360-Lab2
We have created two thread-safe classes, ClientQueue and MessageBox. 
ClientQueue will store all the client objects and make sure no conflict happens while handle function got called. 
MessageBox controls all the access to the message map. Every 'put', 'list', and 'read' function will need to go through this 
thread safe class so there is no conflicts as well. 
