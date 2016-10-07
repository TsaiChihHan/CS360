#pragma once

#include <mutex>
#include <queue>
#include "client_object.h"

using namespace std;

class ClientQueue {
public:
  ClientQueue();
  ~ClientQueue();
  void push_back(ClientObject);
  ClientObject pop_front();
  int size();
  bool empty();
  bool is_full();
  void full_wait();
  void full_signal();
  void not_empty_wait();
  void not_empty_signal();

private:
  queue<ClientObject> queue;
  mutex m;
  condition_variable full;
  condition_variable not_empty;
}
