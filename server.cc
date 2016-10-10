#include "server.h"
#include "message.h"

Server::Server(int port) {
    // setup variables
    port_ = port;
    buflen_ = 1024;
    // buf_ = new char[buflen_+1];
    // char* buf_ = new char[buflen_+1];
}

Server::~Server() {
    // delete buf_;
}

void
Server::run() {
    // create and run the server
    create();
    serve();
}

void
Server::create() {
    struct sockaddr_in server_addr;

    // setup socket address structure
    memset(&server_addr,0,sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port_);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    // create socket
    server_ = socket(PF_INET,SOCK_STREAM,0);
    if (!server_) {
        perror("socket");
        exit(-1);
    }

    // set socket to immediately reuse port when the application closes
    int reuse = 1;
    if (setsockopt(server_, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        perror("setsockopt");
        exit(-1);
    }

    // call bind to associate the socket with our local address and
    // port
    if (bind(server_,(const struct sockaddr *)&server_addr,sizeof(server_addr)) < 0) {
        perror("bind");
        exit(-1);
    }

    // convert the socket to listen for incoming connections
    if (listen(server_,SOMAXCONN) < 0) {
        perror("listen");
        exit(-1);
    }
}

void
Server::close_socket() {
    close(server_);
}

void
Server::work() {
  while(1) {
    ClientObject c = queue.pop();
    if(handle(c))
      queue.push(c);
  }
}

void
Server::serve() {
    // setup client
    int client;
    struct sockaddr_in client_addr;
    socklen_t clientlen = sizeof(client_addr);

    // keep track of vectors
    vector<thread> threads;

    for (int i=0; i < 10; i++) {
        // create thread
        threads.push_back(thread(&Server::work, this));
    }

      // accept clients
    while ((client = accept(server_,(struct sockaddr *)&client_addr,&clientlen)) > 0) {
        cout << "client => " << client << endl;
        queue.push(ClientObject(client));
    }

    close_socket();
}

void
Server::parse_request(int client,bool& success, string request, string& cache) {
  stringstream ss;
  string command, name, subject;
  int length, index;
  command = "";
  name = "";
  subject = "";
  length = -1;
  index = -1;

  ss << request;
  ss >> command;
  if (command == "put") {
      ss >> name >> subject >> length;
      handle_put(client, success, name, subject, length, cache);
  }
  else if (command == "list") {
      ss >> name;
      handle_list(client, success, name);
  }
  else if (command == "get") {
      ss >> name >> index;
      handle_get(client, success, name, index);
  }
  else if (command == "quit") {
      handle_quit(client, success);
  }
  else if (command == "reset") {
      handle_reset(client, success);
  }
  else {
      success = send_response(client, "error command\n");
  }
}

void
Server::handle_put(int client, bool& success, string name, string subject, int length, string& cache) {
  Message message = Message(name, subject, length);
  if (name == "" || subject == "" || length == -1) {
    success = send_response(client, "error command\n");
    return;
  }
  if (message.needed())
      get_value(client, message, cache);

  if (user_map.containsKey(message.getName())) {
    user_map.push_back_message(message.getName(),message);
    success = send_response(client, "OK\n");
  }
  else {
    std::vector<Message> v;
    v.push_back(message);
    user_map.insert(std::pair<string, vector<Message> >(message.getName(), v));
    success = send_response(client, "OK\n");
  }
}

void
Server::handle_get(int client, bool& success, string name, int index) {
  //cout << "Command: get" << endl;
  if (index == -1){
      send_response(client, "error \n");
      return;
  }
  std::map<string, vector<Message> >:: iterator it;
  it = user_map.find(name);
  if (!user_map.containsKey(name)){
      send_response(client, "error can't find the person\n");
      return;
  }
  if (index > user_map[name].size() || index < 1){
      // cout << "7" << endl;
      send_response(client, "error can't find the message\n");
      return;
  }
  send_response(client, user_map.get_message(name,index));
}

void
Server::handle_list(int client, bool& success, string name) {
  int count = 0;

  if (!user_map.containsKey(name)) {
      send_response(client, "error can't find the person\n");
      return;
  }

  success = send_response(client, user_map.list_messages(name));
}

void
Server::handle_quit(int client, bool& success) {
  success = send_response(client, "quit\n");
}

void
Server::handle_reset(int client, bool& success) {
  user_map.clear();
  success = send_response(client, "OK\n");
}

bool
Server::handle(ClientObject c) {
    // loop to handle all requests
    while (1) {

        bool success;
        // get a request
        string request = get_request(c.getSocket(), c.cache);

        // break if client is done or an error occurred
        if (request.empty())
            return false;

        parse_request(c.getSocket(), success, request, c.cache);

        // break if an error occurred
        if (not success)
            return false;
    }
    close(c.getSocket());
    cout << c.getSocket() << " closed" << endl;
    return true;
}

void Server::get_value(int client, Message& message, string& cache){
    char* buf_ = new char[buflen_+1];
    while(cache.size() < message.getLength()){
        int nread = recv(client,buf_,1024,0);
        if (nread < 0) {
            if (errno == EINTR)
                // the socket call was interrupted -- try again
                continue;
            else
                // an error occurred, so break out
                return;
        } else if (nread == 0) {
            // the socket is closed
            cout << "socket is closed" << endl;
            return;
        }
        cache.append(buf_,nread);
    }
    message.setValue(cache);
    cache = "";
    delete buf_;
}


bool Server::handle_message(int client, Message message){
    return send_response(client, message.getValue());
}

string
Server::get_request(int client, string& cache) {
    char* buf_ = new char[buflen_+1];
    string request = "";
    // read until we get a newline
    while (request.find("\n") == string::npos) {
        memset(buf_,0,buflen_);
        int nread = recv(client,buf_,1024,0);
        if (nread == 0)
        cout << "socket " << client << " => nread:" << nread << endl;
        if (nread < 0) {
            if (errno == EINTR)
                // the socket call was interrupted -- try again
                continue;
            else
                // an error occurred, so break out
                return "";
        } else if (nread == 0) {
            // the socket is closed
            return "";
        }
        // be sure to use append in case we have binary data
        request.append(buf_,nread);
    }

    int pos = request.find("\n");
    cache = request.substr(pos + 1);
    // a better server would cut off anything after the newline and
    // save it in a cache
    delete buf_;
    return request.substr(0, pos);
}

bool
Server::send_response(int client, string response) {
    // prepare to send response
    const char* ptr = response.c_str();
    int nleft = response.length();
    int nwritten;
    // loop to be sure it is all sent
    while (nleft) {
        if ((nwritten = send(client, ptr, nleft, 0)) < 0) {
            if (errno == EINTR) {
                // the socket call was interrupted -- try again
                continue;
            } else {
                // an error occurred, so break out
                perror("write");
                return false;
            }
        } else if (nwritten == 0) {
            // the socket is closed
            return false;
        }
        nleft -= nwritten;
        ptr += nwritten;
    }
    return true;
}
