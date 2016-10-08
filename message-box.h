#pragma once

#include <map>
#include <vector>
#include <mutex>
#include <string>
#include "message.h"

using namespace std;


class MessageBox {
public:
  MessageBox();
  ~MessageBox();
  std::map<string, vector<Message> >:: iterator find(string);
  std::map<string, vector<Message> >:: iterator end();
  void insert(std::pair<std::string, vector<Message> >);
  void clear();

private:
  map<std::string,std::vector<Message> > user_messages_map;
  static std::mutex m;
};
