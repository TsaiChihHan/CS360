#pragma once
#include <iostream>
#include <sstream>
#include <string>

using namespace std;


class Command {
public:
	Command(); 
	Command(string input); 
	~Command(){}; 
	string command; 
	string user; 
	string subject; 
	string message; 
	int length; 
	int index; 
	string toString(); 



  }; 