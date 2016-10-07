#pragma once

#include <iostream>
#include <string>

using namespace std;

class ClientObject {
public:
  ClientObject();
  ClientObject(int);
  ~ClientObject();

  int getSocket();
  string getCache();
  void setCache(string);

private:
  int socket_num;
  string cache;
}
