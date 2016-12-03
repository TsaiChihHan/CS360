import errno
import select
import socket
import sys
import traceback
from client import Client
from time import time, gmtime, strftime

class Poller:
    """ Polling server """
    def __init__(self,port):
        self.host = ""
        self.port = port
        self.open_socket()
        self.clients = {}
        self.size = 1024
        self.messages = {}
        self.keys = {}

    def open_socket(self):
        """ Setup the socket for incoming clients """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
            self.server.setblocking(0)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        """ Use poll() to handle each incoming client."""
        self.poller = select.epoll()
        self.pollmask = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        self.poller.register(self.server,self.pollmask)
        while True:
            # poll sockets
            try:
                fds = self.poller.poll(timeout=1)
            except:
                return
            for (fd,event) in fds:
                # handle errors
                if event & (select.POLLHUP | select.POLLERR):
                    self.handleError(fd)
                    continue
                # handle the server socket
                if fd == self.server.fileno():
                    self.handleServer()
                    continue
                # handle client socket
                result = self.handleClient(fd)
            close_idle_socket()

    def handleError(self,fd):
        self.poller.unregister(fd)
        if fd == self.server.fileno():
            # recreate server socket
            self.server.close()
            self.open_socket()
            self.poller.register(self.server,self.pollmask)
        else:
            # close the socket
            self.clients[fd].close()
            del self.clients[fd]

    def handleServer(self):
        # accept as many clients as possible
        while True:
            try:
                (client,address) = self.server.accept()
            except socket.error, (value,message):
                # if socket blocks because no clients are available,
                # then return
                if value == errno.EAGAIN or errno.EWOULDBLOCK:
                    return
                print traceback.format_exc()
                sys.exit()
            # set client socket to be non blocking
            client.setblocking(0)
            self.clients[client.fileno()] = Client(client,"",time())
            self.poller.register(client.fileno(),self.pollmask)

    def handleClient(self,fd):

        try:
            data = self.clients[fd].socket.recv(self.size)
        except socket.error, (value,message):
            # if no data is available, move on to another client
            if value == errno.EAGAIN or errno.EWOULDBLOCK:
                return
            print traceback.format_exc()
            sys.exit()
        if data:
            self.clients[fd].cache += data
            message = self.read_message(fd)
            if not message:
                return
            self.handle_message(message,fd)    
            #self.clients[fd].socket.send(data)
        else:
            self.poller.unregister(fd)
            self.clients[fd].socket.close()
            del self.clients[fd]

    def read_message(self,fd):
        index = self.clients[fd].cache.find("\n")
        if index == "-1" or index == -1:
            return None
        message = self.clients[fd].cache[0:index+1]
        self.clients[fd].cache = self.clients[fd].cache[index+1:]
        return message

    def handle_message(self,message,fd):
        response = self.parse_message(message,fd)
        self.send_response(response,fd)

    def parse_message(self,message,fd):
        fields = message.split()
        if not fields:
            return('error invalid message\n')
        if fields[0] == 'reset':
            self.messages = {}
            return "OK\n"
        if fields[0] == 'put':
            try:
                name = fields[1]
                subject = fields[2]
                length = int(fields[3])
            except:
                return('error invalid message\n')
            data = self.read_put(length, fd)
            if data == None:
                return 'error could not read entire message\n'
            self.store_message(name,subject,data)
            return "OK\n"
        if fields[0] == 'list':
            try:
                name = fields[1]
            except:
                return('error invalid message\n')
            subjects,length = self.get_subjects(name)
            response = "list %d\n" % length
            response += subjects
            return response
        if fields[0] == 'get':
            try:
                name = fields[1]
                index = int(fields[2])
            except:
                return('error invalid message\n')
            subject,data = self.get_message(name,index)
            if not subject:
                return "error no such message for that user\n"
            response = "message %s %d\n" % (subject,len(data))
            response += data
            return response
        if fields[0] = "store_key":
            try:
                name = fields[1]
                length = int(fieldsp[2])
            except:
                return('error invalid message\n')
            key = read_put(length, fd)
            if key == None:
                return 'error could not read entire message\n'
            self.store_key(name,key)
            return "OK\n"
        if fields[0] = 'get_key':
            try:
                name = fields[1]
            except:
                return('error invalid message\n')
            key = get_key(name)
            if not key:
                return "error no such user\n"
            response = "key %d\n%s" %(len(key),key)
            return response
        return('error invalid message\n')
    
    def store_message(self,name,subject,data):
        if name not in self.messages:
            self.messages[name] = []
        self.messages[name].append((subject,data))

    def store_key(self,name,key):
        self.keys[name] = key

    def get_subjects(self,name):
        if name not in self.messages:
            return "",0
        response = ["%d %s\n" % (index+1,message[0]) for index,message in enumerate(self.messages[name])]
        return "".join(response),len(response)

    def get_message(self,name,index):
        if index <= 0:
            return None,None
        try:
            return self.messages[name][index-1]
        except:
            return None,None

    def get_key(self,name):
        if name not in self.keys:
            return None
        else:
            return self.keys[name]

    def read_put(self,length,fd):
        data = self.clients[fd].cache
        while len(data) < length:
            d = self.client.recv(self.size)
            if not d:
                return None
            data += d
        if len(data) > length:
            self.cache = data[length:]
            data = data[:length]
        else:
            self.clients[fd].cache = ''
        return data

    def send_response(self,response,fd):
        self.clients[fd].socket.sendall(response)

    def close_idle_socket(self):
        current_time = time()
        for fd in self.clients:
            if current_time - self.clients[fd].request_time > 5
                self.clients[fd].socket.close()
                del self.clients[fd]