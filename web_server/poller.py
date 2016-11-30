import errno
import select
import socket
import sys
import os
import traceback
from time import time, gmtime, strftime
from http_parser.parser import HttpParser


class Client:
	def __init__(self, socket, cache, request_time):
		self.cache = ""
		self.socket = socket
		self.request_time = request_time

def get_time(t):
	gmt = gmtime(t)
	format = "%a, %d %b %Y %H:%M:%S GMT"
	time_string = strftime(format, gmt)
	return time_string

class Poller:
	""" Polling server """
	def __init__(self,port,debug):
		self.host = ""
		self.port = port
		self.debug = debug
		self.open_socket()
		self.clients = {}
		self.size = 1024
		self.timeout = 1
		self.config = "web.conf"
		self.hosts = {}
		self.media = {}
		self.parameters = {}
		self.web_config()

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

	def web_config(self):
		try:
			f = open(self.config, 'r')
		except (OSerror, IOError) as e:
			print str(e)
			sys.exit()
		for line in f:
			if len(line) > 1:
				line = line.rstrip("\n").split(" ")
				if line[0] == "host":
					self.hosts[line[1]] = line[2]
				elif line[0] == "media":
					self.media[line[1]] = line[2]
				elif line[0] == "parameter":
					self.parameters[line[1]] = line[2]
					if line[1] == "timeout":
						self.timeout = line[2]
				else:
					if self.debug:
						print "invalid input in web.conf"
		f.close()
		if self.debug:
			print "\nhosts: ", self.hosts
			print "\nmedia:", self.media
			print "\nparameters: ", self.parameters
			print "\ntimeout: ", self.timeout

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
			current_time = time()
			self.close_idle_socket(current_time)
			
	def handleError(self,fd):
		self.poller.unregister(fd)
		if fd == self.server.fileno():
			# recreate server socket
			self.server.close()
			self.open_socket()
			self.poller.register(self.server,self.pollmask)
		else:
			# close the socket
			self.clients[fd].socket.close()
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
	
	def get_200(self,fd,entity_body, path, method):
		headers = "HTTP/1.1 200 Ok\r\nDate: %s\r\nLast-Modified: %s\r\nContent-Length: %d\r\nContent-Type: %s\r\nServer: %s\r\n\r\n" %(get_time(self.clients[fd].request_time),get_time(os.stat(path).st_mtime),len(entity_body), self.media[path.split(".")[-1]],"Apache")
		if method.upper() == "HEAD":
			return headers
		else:
			return headers + entity_body
	
	def get_206(self,fd,entity_body,path, range):
		range = range.split("=")[-1].split("-")
		entity_body = entity_body[int(range[0]):int(range[-1])+1]
		headers = "HTTP/1.1 206 Partial Content\r\nDate: %s\r\nLast-Modified: %s\r\nContent-Length: %d\r\nContent-Type: %s\r\nServer: %s\r\n\r\n" %(get_time(self.clients[fd].request_time),get_time(os.stat(path).st_mtime),len(entity_body.encode("utf8")), self.media[path.split(".")[-1]],"Apache")
		return headers + entity_body

	def get_400(self,fd):
		entity_body = "<!DOCTYPE>\n<html><head>\n<title>400 Bad Request</title>\n<head><body>\n<h1>Bad Request</h1>\n<p>Your browser sent a request that this server could not understand.<br />\n</p>\n<hr>\n</body></html>\nConnection closed by foreign host."
		headers = "HTTP/1.1 400 Bad Request\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nServer: Appache\r\n\r\n" %(get_time(self.clients[fd].request_time),len(entity_body))
		return headers + entity_body

	def get_403(self,fd):
		entity_body = "<!DOCTYPE>\n<html><head>\n<title>403 Forbidden</title>\n<head><body>\n<h1>403 Forbidden</h1>\n<hr>\n</body></html>\nConnection closed by foreign host."
		headers = "HTTP/1.1 403 Forbidden\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nServer: Appache\r\n\r\n" %(get_time(self.clients[fd].request_time),len(entity_body))
		return headers + entity_body

	def get_404(self,fd):
		entity_body = "<!DOCTYPE>\n<html><head>\n<title>404 Not Found</title>\n<head><body>\n<h1>404 Not Found</h1>\n<hr>\n</body></html>\nConnection closed by foreign host."
		headers = "HTTP/1.1 404 Forbidden\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nServer: Appache\r\n\r\n" %(get_time(self.clients[fd].request_time),len(entity_body))
		return headers + entity_body

	def get_500(self,fd):
		entity_body = "<!DOCTYPE>\n<html><head>\n<title>500 Internal Server Error</title>\n<head><body>\n<h1>500 Internal Server Error</h1>\n<hr>\n</body></html>\nConnection closed by foreign host."
		headers = "HTTP/1.1 500 Internal Server Error\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nServer: Appache\r\n\r\n" %(get_time(self.clients[fd].request_time),len(entity_body))
		return headers + entity_body

	def get_501(self,fd):
		entity_body = "<!DOCTYPE>\n<html><head>\n<title>503 Not Implemented</title>\n<head><body>\n<h1>503 Not Implemented</h1>\n<hr>\n</body></html>\nConnection closed by foreign host."
		headers = "HTTP/1.1 501 Not Implemented\r\nDate: %s\r\nContent-Type: text/html\r\nContent-Length: %d\r\nServer: Appache\r\n\r\n" %(get_time(self.clients[fd].request_time),len(entity_body))
		return headers + entity_body
		
	def get_path(self,parser):
		path = ""
		host = self.hosts.get(parser.get_headers().get('Host'))
		if host:
			path = host
		else:
			path = str(self.hosts["default"])

		url = str(parser.get_path())
		if url == "/":
			path += "/index.html"
		else:
			path += url
		return path

	def close_idle_socket(self, current_time):
		for fd in self.clients:
			if current_time - self.clients[fd].request_time > self.timeout:
				self.clients[fd].socket.close()
				del self.clients[fd]
	
	def handleClient(self,fd):
		while True:
			try:
				data = self.clients[fd].socket.recv(self.size)
			except socket.error, (value,message):
				# if no data is available, move on to another client
				if value == errno.EAGAIN or errno.EWOULDBLOCK:
					break
				else:
					print traceback.format_exc()
					sys.exit()
			if data:
				if self.debug:
					print "data = ", data
				self.clients[fd].cache += data
				#print self.clients[fd].cache
				if "\r\n\r\n" in self.clients[fd].cache:
					p = HttpParser()
					p.execute(self.clients[fd].cache,len(self.clients[fd].cache))
					self.clients[fd].cache = ""
					response = ""

					if p.get_errno() != 0:
						response = self.get_400(fd)
					elif p.get_method().upper() != "GET" and p.get_method().upper() != "HEAD":
						response = self.get_501(fd)

					path = self.get_path(p)
					#print path
					try:
						f = open(path)
					except IOError as (err,strerror):
						if err == 13:
							response = self.get_403(fd)
						elif err == 2:
							response = self.get_404(fd)
						else:
							if response == "":
								response = self.get_500(fd)
					if response == "":
						range = p.get_headers().get("Range")
						if range:
							response = self.get_206(fd, f.read(), path, range)
						else:
							response = self.get_200(fd, f.read(), path, p.get_method())
					if self.debug:
						print response
					self.clients[fd].socket.send(response)
					break
				else:
					continue

			else:
				self.poller.unregister(fd)
				self.clients[fd].socket.close()
				del self.clients[fd]
				break
