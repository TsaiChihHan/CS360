#include "message.h"

Message::Message() {}

Message::Message(string name, string subject, int length) {
	this->name = name;
	this->subject = subject;
	this->length = length;
}

Message::~Message() {}

bool
Message::needed(){
	if (value.size() == length){
		return false;
	}else{
		return true;
	}
}

string
Message::getName() {
	return this->name;
}

string
Message::getSubject() {
	return this->subject;
}

string
Message::getValue() {
	return this->value;
}

int
Message::getLength() {
	return this->length;
}

void
Message::setName(string name) {
	this->name = name;
}

void
Message::setSubject(string subject) {
	this->subject = subject;
}

void
Message::setValue(string value) {
	this->value = value;
}

void
Message::setLength(int length) {
	this->length = length;
}
