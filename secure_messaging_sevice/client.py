class Client:
	def __init__(self, socket, cache, request_time):
		self.cache = ""
		self.socket = socket
		self.request_time = request_time