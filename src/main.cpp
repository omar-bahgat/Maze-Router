#include <iostream>
#include "route.hpp"

using namespace std;

int main() {

    string filename = "";
    cout << "Enter the input file name (without extension): ";
    cin >> filename;

    readInputFile(filename);

    processNets();

    showRoutingInfo();

    writeOutput(filename);

    return 0;
}
