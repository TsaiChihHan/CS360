import errno
import select
import socket
import sys
import os
import traceback
from time import time, gmtime, strftime
from http_parser.parser import HttpParser

def get_time(t):
    gmt = gmtime(t)
    format = "%a, %d %b %Y %H:%M:%S GMT"
    time_string = strftime(format, gmt)
    return time_string

class Poller:
    """ Polling server """
    def __init__(self,port):
        self.host = ""
        self.port = port
        self.open_socket()
        self.clients = {}
        self.size = 1024
        self.cache = ""

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
            self.clients[client.fileno()] = client
            self.poller.register(client.fileno(),self.pollmask)

    def get_time(self,t):
        gmt = gmtime(t)
        format = "%a, %d %b %Y %H:%M:%S GMT"
        time_string = strftime(format, gmt)
        return time_string

    def handleClient(self,fd):
        try:
            data = self.clients[fd].recv(self.size)
        except socket.error, (value,message):
            # if no data is available, move on to another client
            if value == errno.EAGAIN or errno.EWOULDBLOCK:
                return
            print traceback.format_exc()
            sys.exit()

        if data:
            print data
            self.cache += data
            print self.cache
            if "\r\n\r\n" in self.cache:
                p = HttpParser()
                p.execute(self.cache,len(self.cache))

                # Get the date of the request
                t = time()


                # Check whether the method is GET
                if p.get_method().upper() == "" or p.get_path() == "":
                    print "400 Bad Request"
                    self.clients[fd].send("HTTP/1.1 400 Bad Request\r\nDate: " + get_time(t) + "\r\nContent-Length: 234\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE>\n<html><head>\n<title>400 Bad Request</title>\n<head><body>\n<h1>Bad Request</h1>\n<p>Your browser sent a request that this server could not understand.<br />\n</p>\n<hr>\n</body></html>\nConnection closed by foreign host.")
                if p.get_method().upper() != "GET":
                    self.clients[fd].send("HTTP/1.1 503 Not Implemented\r\nDate: " + get_time(t) + "\r\nContent-Length: 163\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE>\n<html><head>\n<title>503 Not Implemented</title>\n<head><body>\n<h1>503 Not Implemented</h1>\n<hr>\n</body></html>\nConnection closed by foreign host.")
                path = ""
                with open('web.conf', 'r') as f:
                    default_host = ""
                    for line in f:
                        fields = line.rstrip("\n").split(" ")
                        if fields[0] == "host":
                            if fields[1] == "default":
                                default_host = fields[2]
                            elif fields[1] == p.get_headers()['Host']:
                                path = fields[2]
                    if path == "":
                        path = default_host
                if p.get_path() == "/":
                    path += "/index.html"
                else:
                    path += p.get_path()

                try:
                    open(path)
                except IOError as (errno,strerror):
                    if errno == 13:
                        self.clients[fd].send("HTTP/1.1 403 Forbidden\r\n" + "Date: " + get_time(t) + "\r\nContent-Length: 151\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE>\n<html><head>\n<title>403 Forbidden</title>\n<head><body>\n<h1>403 Forbidden</h1>\n<hr>\n</body></html>\nConnection closed by foreign host.")
                    elif errno == 2:
                        self.clients[fd].send("HTTP/1.1 404 Forbidden\r\n" + "Date: " + get_time(t) + "\r\nContent-Length: 151\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE>\n<html><head>\n<title>404 Not Found</title>\n<head><body>\n<h1>404 Not Found</h1>\n<hr>\n</body></html>\nConnection closed by foreign host.")
                    else:
                        self.clients[fd].send("HTTP/1.1 500 Internal Server Error\r\n" + "Date: " + get_time(t) + "\r\nContent-Length: 175\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE>\n<html><head>\n<title>500 Internal Server Error</title>\n<head><body>\n<h1>500 Internal Server Error</h1>\n<hr>\n</body></html>\nConnection closed by foreign host.")
                self.clients[fd].send("HTTP/1.1 200 Ok\r\nDate: %s\r\nLast-Modified: %s\r\nContent-Length: %d\r\nContent-Type: %s\r\nServer: %s\r\n\r\n%s" % (get_time(t),get_time(os.stat(path).st_mtime),os.stat(path).st_size, "text/html","Apache",open(path,"r").read()))
            else:
                self.clients[fd].send("incomplete\r\n")

        else:
            self.poller.unregister(fd)
            self.clients[fd].close()
            del self.clients[fd]
