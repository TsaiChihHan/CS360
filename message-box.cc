#include "message.h"

MessageBox::MessageBox() {}

MessageBox::~MessageBox() {}

std::map<string, vector<Message> >:: iterator
MessageBox::find(string key) {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it = map.find(key);
  return it;
}

std::map<string, vector<Message> >:: iterator
MessageBox::end() {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it = map.end();
  return it;
}

void
MessageBox::insert(std::pair<std::string, vector<Message> > pair) {
  unique_lock<mutex> lock(m);
  map.insert(pair);
}

void
MessageBox::clear() {
  unique_lock<mutex> lock(m);
  map.clear();
}
