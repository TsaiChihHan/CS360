#include "client_queue.h"

ClientQueue::ClientQueue() {}

ClientQueue::~ClientQueue() {}

void
ClientQueue::push(ClientObject c) {
    unique_lock<mutex> lock(m);
    client_queue.push(c);
    return;
}

ClientObject
ClientQueue::pop() {
    unique_lock<mutex> lock(m);
    ClientObject c = client_queue.front();
    client_queue.pop();
    return c;
}

int
ClientQueue::size() {
    unique_lock<mutex> lock(m);
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

void
ClientQueue::full_signal() {
  full.notify_one();
}

void
ClientQueue::full_wait() {
  full.wait();
}

void
ClientQueue::not_empty_signal() {
  not_empty.notify_one();
}

void
ClientQueue::not_empty_wait() {
  not_empty.wait();
}
