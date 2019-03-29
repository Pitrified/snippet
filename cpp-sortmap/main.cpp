#include <iostream>
#include <vector>
#include <functional>
#include <map>
#include <set>

using namespace std;

int main(int argc, char** argv)
{
    map<int, float> errori;
    errori[1] = 0.0;
    errori[7] = 0.77777777;
    errori[3] = 3.0;
    errori[6] = 2.0;
    errori[9] = 0.4;
    cout << errori[7] << endl;

    for ( map<int,float>::value_type& x : errori) {
        cout << x.first << " : " << x.second << endl;
    }

    cout << errori.count(1) << endl;
    cout << errori.count(2) << endl;

    // dichiara un tipo che prende due coppie e ritorna bool
    typedef function<bool(pair<int,float>, pair<int,float>)> myCompType;
    // lambda function che compara i valori delle pair
    myCompType myComp = 
        [](pair<int,float> e1, pair<int,float> e2) {
            return e1.second < e2.second;
        };

    // set che usa il comparatore come modo di ordinamento
    set<pair<int,float>, myCompType> setError(
            errori.begin(), errori.end(), myComp);

    // il set ordinato come vuoi
    for (pair<int,float> e : setError ) {
        cout << e.first << " : " << e.second << endl;
    }
}
