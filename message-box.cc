#include "message-box.h"

MessageBox::MessageBox() {}

MessageBox::~MessageBox() {}

mutex MessageBox::m;

vector<Message>
MessageBox::operator[](string key) {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it;
  it = user_messages_map.find(key);
  return it->second;
}

void
MessageBox::push_back_message(string key, Message message) {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it;
  it = user_messages_map.find(key);
  it->second.push_back(message);
}

string
MessageBox::get_message(string key, int index) {
  std::map<string, vector<Message> >:: iterator it;
  it = user_messages_map.find(key);
  stringstream ss;
  ss << "message " << it->second[index-1].getSubject() << " " << it->second[index-1].getLength() << endl << it->second[index-1].getValue() ;
  return ss.str();
}

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

bool
MessageBox::containsKey(string key) {
  unique_lock<mutex> lock(m);
  if (user_messages_map.find(key) != user_messages_map.end())
    return true;
  else
    return false;
}

string
MessageBox::list_messages(string key) {
  unique_lock<mutex> lock(m);
  std::map<string, vector<Message> >:: iterator it = user_messages_map.find(key);
  stringstream ss;
  ss << "list " << it->second.size() << endl;
  for (int i = 0; i < it->second.size() ; i++){
      ss << i+1 << " " << it->second[i].getSubject() << endl;
  }
  return ss.str();
}
