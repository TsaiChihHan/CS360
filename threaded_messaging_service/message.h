#pragma once
#include <iostream>
#include <sstream>
#include <string>

using namespace std;


class Message {
public:
		Message();
		Message(string, string, int);
		~Message();

		bool needed();

		string getName();
		string getSubject();
		string getValue();
		int getLength();

		void setName(string);
		void setSubject(string);
		void setValue(string);
		void setLength(int);
private:
    string name;
		string subject;
    string value;
		int length;
};
