#include "message-box.h"

MessageBox::MessageBox() {}

MessageBox::~MessageBox() {}

mutex
MessageBox::m;

std::map<string, vector<Message> >:: iterator
MessageBox::find(string key) {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it = user_messages_map.find(key);
  return it;
}

std::map<string, vector<Message> >:: iterator
MessageBox::end() {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it = user_messages_map.end();
  return it;
}

void
MessageBox::insert(std::pair<std::string, vector<Message> > pair) {
  unique_lock<mutex> lock(m);
  user_messages_map.insert(pair);
}

void
MessageBox::clear() {
  unique_lock<mutex> lock(m);
  user_messages_map.clear();
}
