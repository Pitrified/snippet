#include <iostream>
using namespace std;
int main () {
    cout << "int var = 5\n";
    int var = 5;
    cout << "Address of var variable: &var: ";
    cout << &var << endl;
    cout << "Value   of var variable:  var: ";
    cout << var << endl;
    cout << endl;

    int *pointer;
    pointer = &var; // store address of var in pointer variable
    cout << "Value of var variable:  var: ";
    cout << var << endl;
    cout << "Address stored in pointer variable: ";
    cout << pointer << endl;  // 0xbfc601ac (address of var)
    // access the value at the address in pointer
    cout << "Value of *pointer variable: ";
    cout << *pointer << endl; // 5 (value of var)
    cout << "Address stored in  pointer+1: " << pointer+1 << endl;
    cout << "Value stored in *(pointer+1): " << *(pointer+1) << endl;
    cout << endl;

    int &ref = var;
    int sec = var;
    cout << "Value of &var: " << &var << endl;
    cout << "Value of &ref: " << &ref << endl;
    cout << "Value of &sec: " << &sec << endl;
    cout << "Value of  var: " << var << endl;
    cout << "Value of  ref: " << ref << endl;
    cout << "Value of  sec: " << sec << endl;
    var = 7;
    cout << "Value of &var: " << &var << endl;
    cout << "Value of &ref: " << &ref << endl;
    cout << "Value of &sec: " << &sec << endl;
    cout << "Value of  var: " << var << endl;
    cout << "Value of  ref: " << ref << endl;
    cout << "Value of  sec: " << sec << endl;

    return 0;
}
