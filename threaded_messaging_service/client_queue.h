#pragma once

#include <mutex>
#include <queue>
#include "client_object.h"

using namespace std;

class ClientQueue {
public:
  ClientQueue();
  // ClientQueue(const ClientQueue&);
  ~ClientQueue();
  void push(ClientObject);
  ClientObject pop();
  int size();
  bool empty();
  bool is_full();

  static std::mutex m;
  static std::condition_variable full;
  static std::condition_variable not_empty;

private:
  queue<ClientObject> client_queue;
};
