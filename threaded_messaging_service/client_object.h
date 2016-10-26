#pragma once

#include <iostream>
#include <string>
#include <mutex>
#include <condition_variable>

using namespace std;

class ClientObject {
public:
  ClientObject();
  ClientObject(int);
  ~ClientObject();

  int getSocket();
  string getCache();
  void setCache(string);

  string cache;

private:
  int socket_num;
};
