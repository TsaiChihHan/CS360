#include "client_queue.h"

ClientQueue::ClientQueue() {}

ClientQueue::~ClientQueue() {}

mutex ClientQueue::m;
condition_variable ClientQueue::full;
condition_variable ClientQueue::not_empty;

void
ClientQueue::push(ClientObject c) {
    unique_lock<mutex> lock(m);
    while (is_full()) {
      full.wait(lock);
    }
    client_queue.push(c);
    not_empty.notify_one();
    return;
}

ClientObject
ClientQueue::pop() {
    unique_lock<mutex> lock(m);
    while(client_queue.empty()) {
      not_empty.wait(lock);
    }
    ClientObject c = client_queue.front();
    client_queue.pop();
    full.notify_one();
    return c;
}

int
ClientQueue::size() {
    // unique_lock<mutex> lock(m);
    int size = client_queue.size();
    return size;
}

bool
ClientQueue::is_full() {
  if (size() >= 200) {
    return true;
  }
  else {
    return false;
  }
}

bool
ClientQueue::empty() {
  if (size() == 0) return true;
  else return false;
}

// void
// ClientQueue::full_signal() {
//   full.notify_one();
// }
//
// void
// ClientQueue::full_wait() {
//   full.wait();
// }
//
// void
// ClientQueue::not_empty_signal() {
//   not_empty.notify_one();
// }
//
// void
// ClientQueue::not_empty_wait() {
//   not_empty.wait();
// }
