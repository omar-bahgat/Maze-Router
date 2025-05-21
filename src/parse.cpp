#include "parse.hpp"
#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;

const int INF = 1e9;
int ROWS, COLS, VIA_COST, NON_PREF_COST;

vector<vector<vector<int>>> grid;               // marks obstacles and cells where route exists
map<int, vector<tuple<int, int, int>>> nets;    // net_id -> vector of coordinates (layer, x, y)

tuple<int, int, int> parseObstacle(const string& line) {
    stringstream ss(line);
    int layer, x, y;
    char ch;
    while (ss >> ch && ch != '(');
    ss >> layer >> ch >> x >> ch >> y;

    return make_tuple(layer, x, y);
}

void parseNet(string& line) {
    stringstream ss(line);
    string net_name;
    ss >> net_name;
    int net_id = stoi(net_name.substr(3));

    char ch;
    int layer, x, y;
    vector<tuple<int, int, int>> coord;
    while (ss >> ch && ch == '(') {
        ss >> layer >> ch >> x >> ch >> y >> ch;
        coord.push_back(make_tuple(layer, x, y));
    }
    nets[net_id] = coord;
}

bool beginsWith(const string& str, const string& prefix) {
    return (str.substr(0, prefix.size()) == prefix);
}

void readInputFile(const string& filename) {
    string filepath = "../Tests/" + filename + ".txt";
    ifstream file(filepath);

    string line;
    getline(file, line);
    stringstream ss(line);

    char ch;
    ss >> ROWS >> ch >> COLS >> ch >> VIA_COST >> ch >> NON_PREF_COST;

    grid = vector<vector<vector<int>>>(2, vector<vector<int>>(ROWS, vector<int>(COLS, 0)));

    while (getline(file, line)) {
        if (beginsWith(line, "OBS")) {
            auto [layer, x, y] = parseObstacle(line);
            grid[layer - 1][x][y] = -1;
        }
        else if (beginsWith(line, "net")) {
            parseNet(line);
        }
        else {
            cout << "Invalid input";
            exit(1);
        }
    }
}


// 100, 100, 5, 100
// OBS (1, 20, 20)
// OBS (1, 40, 40)
// OBS (1, 60, 60)
// OBS (1, 80, 80)
// OBS (1, 30, 70)
// OBS (1, 70, 30)
// OBS (1, 50, 50)
// OBS (1, 55, 55)
// net1 (1, 0, 0) (1, 20, 20) (2, 40, 40) (2, 60, 60)
// net2 (2, 99, 99) (2, 80, 80) (1, 60, 60) (1, 40, 40)
// net3 (1, 5, 95) (1, 30, 70) (2, 55, 55) (2, 80, 20)
// net4 (2, 25, 25) (2, 50, 50) (1, 70, 30) (1, 90, 10)
