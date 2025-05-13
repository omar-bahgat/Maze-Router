#pragma once

#include "parse.hpp"
#include <queue>
#include <vector>
#include <tuple>
#include <map>

using namespace std;

// node with lowest cost so far
struct Node {
    int cost, layer, x, y;
    bool operator>(const Node& other) const {
        return cost > other.cost;
    }
};


vector<tuple<int, int, int>> routeNet(tuple<int, int, int> src, tuple<int, int, int> dest);
void processNets();
void writeOutput(const string& filename);
void showRoutingInfo();
