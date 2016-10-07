#include "command.h"

Command::Command(){}

Command::Command(string input){
	stringstream ss ;
	ss << input; 
	ss >> this->command; 
	if (this->command == "send"){
		ss >> this->user; 
		ss >> this->subject;
	}
	else if (this->command == "read"){
		ss >> this->user; 
		ss >> this->index; 
	}else if (this->command == "list"){
		ss >> this->user; 
	}else if(this->command == "quit"){

	}else{
		cout << "error, can't recognize the command" << endl; 
	}

}

string Command::toString(){
	stringstream ss; 
	if (command == "send"){
		ss << "put " << user << " " << subject << " " << message.size() << endl << message ; 
	}else if (command == "list"){
		ss << "list " << user << endl;
	}else if (command == "read"){
		ss << "get " << user << " " << index << endl;
	}else if (command == "quit"){
		ss << "quit" << endl;
	}
	return ss.str(); 
}