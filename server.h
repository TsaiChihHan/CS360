#pragma once

#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <sstream>
#include <iostream>
#include <vector>
#include <map>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <string>

#include "message-box.h"
#include "client_queue.h"

using namespace std;

class Server {
public:
    Server(int port);
    ~Server();
    void run();

private:
    void create();
    void close_socket();
    void work();
    void serve();
    void handle(ClientObject);
    string get_request(int, string&);
    bool send_response(int, string);
    void get_value(int client, Message& message, string&);
    void parse_request(string request, string&);
    bool handle_message(int client, Message message);

    void parse_request(int client, bool& success, string request, string&);
    void handle_put(int client, bool& success, string name, string subject,int length, string&);
    void handle_get(int client, bool& success, string name, int index);
    void handle_list(int client, bool& success, string name);
    void handle_quit(int client, bool& success);
    void handle_reset(int client, bool& success);


    //Message parse_request(string request, string name);

    int port_;
    int server_;
    int buflen_;
    char* buf_;
    string cache;
    MessageBox user_map;
    ClientQueue queue;
};
