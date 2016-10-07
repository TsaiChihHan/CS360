#include "client_queue.h"

ClientQueue::ClientQueue() {}

ClientQueue::~ClientQueue() {}

void
ClientQueue::push_back(ClientObject c) {
    unique_lock<mutex> lock(m);
    queue.push_back(c);
    return;
}

ClientObject
ClientQueue::pop_front() {
    unique_lock<mutex> lock(m);
    ClientObject c = queue.pop_front();
    return c;
}

int
ClientQueue::size() {
    unique_lock<mutex> lock(m);
    int size = queue.size();
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
  full.wait(&m);
}

void
ClientQueue::not_empty_signal() {
  not_empty.notify_one();
}

void
ClientQueue::not_empty_wait() {
  not_empty.wait(&m);
}
