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
  // void full_wait();
  // void full_signal();
  // void not_empty_wait();
  // void not_empty_signal();

  static std::mutex m;
  static std::condition_variable full;
  static std::condition_variable not_empty;

private:
  queue<ClientObject> client_queue;
};
