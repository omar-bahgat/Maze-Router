#include <iostream>
#include "route.hpp"

using namespace std;

int main() {

    string filename = "";
    cout << "Enter the input file name (without extension): ";
    cin >> filename;

    char input;
    cout << "Enable net reordering heuristic? (y/n): ";
    cin >> input;
    ENABLE_NET_REORDERING = (input == 'y' || input == 'Y');

    readInputFile(filename);

    processNets();

    showRoutingInfo();

    writeOutput(filename);

    return 0;
}
