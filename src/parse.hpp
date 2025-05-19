#pragma once

#include <string>
#include <vector>
#include <map>
#include <tuple>

using namespace std;

extern const int INF;
extern int ROWS, COLS, VIA_COST, NON_PREF_COST;

extern vector<vector<vector<int>>> grid;
extern map<int, vector<tuple<int, int, int>>> nets;

tuple<int, int, int> parseObstacle(const string& line);
void parseNet(string& line);
bool beginsWith(const string& str, const string& prefix);
void readInputFile(const string& filename);
