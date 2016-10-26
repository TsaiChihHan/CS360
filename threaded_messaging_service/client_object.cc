#include "client_object.h"\

ClientObject::ClientObject() {}

ClientObject::ClientObject(int socket): socket_num(socket), cache("") {

}

ClientObject::~ClientObject() {}

int
ClientObject::getSocket() {
  return socket_num;
}

string
ClientObject::getCache() {
  return cache;
}

void
ClientObject::setCache(string str) {
    cache = str;
}
