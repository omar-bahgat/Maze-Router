#include "route.hpp"
#include <iostream>
#include <algorithm>
#include <fstream>
#include <unordered_set>

using namespace std;

map<int, vector<tuple<int, int, int>>> routed_paths;

vector<tuple<int, int, int>> reconstructPath(
    const vector<vector<vector<tuple<int, int, int>>>>& prev,
    int startLayer, int startX, int startY,
    int endLayer, int endX, int endY) {

    vector<tuple<int, int, int>> path;
    int l = endLayer, x = endX, y = endY;

    // Backtrack from end to start
    tuple<int, int, int> lastAdded = { -1, -1, -1 }; // To track last added element

    while (l != -1 && !(l == startLayer && x == startX && y == startY)) {
        // Avoid adding consecutive duplicates
        tuple<int, int, int> current = { l + 1, x, y };
        if (current != lastAdded) {
            path.emplace_back(current);
            lastAdded = current;
        }

        auto [pl, px, py] = prev[l][x][y];
        l = pl;
        x = px;
        y = py;
    }

    if (l == startLayer && x == startX && y == startY) {
        tuple<int, int, int> startCell = { startLayer + 1, startX, startY };
        if (startCell != lastAdded) {
            path.emplace_back(startCell);
        }
        reverse(path.begin(), path.end());
        return path;
    }

    return {};
}


vector<tuple<int, int, int>> routeNet(tuple<int, int, int> src, tuple<int, int, int> dest) {
    auto [startLayer, startX, startY] = src;
    auto [endLayer, endX, endY] = dest;

    priority_queue<Node, vector<Node>, greater<Node>> pq;
    vector<vector<vector<int>>> dist(2, vector<vector<int>>(ROWS, vector<int>(COLS, INF)));
    vector<vector<vector<tuple<int, int, int>>>> prev(2,
        vector<vector<tuple<int, int, int>>>(ROWS,
            vector<tuple<int, int, int>>(COLS, { -1, -1, -1 })));

    startLayer--;
    endLayer--;

    pq.push({ 0, startLayer, startX, startY });
    dist[startLayer][startX][startY] = 0;
    prev[startLayer][startX][startY] = { startLayer, startX, startY };

    const vector<tuple<int, int>> dirs = { {-1,0}, {1,0}, {0,-1}, {0,1} };

    while (!pq.empty()) {
        Node curr = pq.top();
        pq.pop();

        if (curr.cost > dist[curr.layer][curr.x][curr.y]) continue;

        // check if we reached the destination
        if (curr.layer == endLayer && curr.x == endX && curr.y == endY) {
            return reconstructPath(prev, startLayer, startX, startY,
                curr.layer, curr.x, curr.y);
        }

        for (auto [dx, dy] : dirs) {
            int nx = curr.x + dx, ny = curr.y + dy;
            if (nx < 0 || nx >= ROWS || ny < 0 || ny >= COLS) continue;
            if (grid[curr.layer][nx][ny] == -1) continue;

            int moveCost = 1;
            // check if the move is preferred or not 
            if ((curr.layer + 1 == 1 && dy != 0) || (curr.layer + 1 == 2 && dx != 0)) {
                moveCost = NON_PREF_COST;
            }

            int newCost = curr.cost + moveCost;
            if (newCost < dist[curr.layer][nx][ny]) {
                dist[curr.layer][nx][ny] = newCost;
                prev[curr.layer][nx][ny] = { curr.layer, curr.x, curr.y };
                pq.push({ newCost, curr.layer, nx, ny });
            }
        }

        // via handling
        int newLayer = 1 - curr.layer;
        if (grid[newLayer][curr.x][curr.y] != -1) {
            int newCost = curr.cost + VIA_COST;
            if (newCost < dist[newLayer][curr.x][curr.y]) {
                dist[newLayer][curr.x][curr.y] = newCost;
                prev[newLayer][curr.x][curr.y] = { curr.layer, curr.x, curr.y };
                pq.push({ newCost, newLayer, curr.x, curr.y });
            }
        }
    }
    return {};
}

void processNets() {

    // loop over all nets
    for (auto& [net_id, pins] : nets) {
        vector<tuple<int, int, int>> full_path;

        // loop over all pins in the net
        for (size_t i = 0; i < pins.size() - 1; i++) {
            // find path from pin i to pin i+1
            auto segment = routeNet(pins[i], pins[i + 1]);

            auto start = segment.begin();
            auto end = segment.end();

            // skip first element to avoid overlap
            if (i > 0 && !segment.empty() && !full_path.empty()) {
                start = segment.begin() + 1;
            }

            // mark visited nodes as obstacles
            for (auto it = start; it != end; it++) {
                auto [layer, x, y] = *it;
                grid[layer - 1][x][y] = -1;
            }

            full_path.insert(full_path.end(), start, end);
        }

        routed_paths[net_id] = full_path;
    }
}


void showRoutingInfo() {
    for (const auto& [net_id, path] : routed_paths) {
        int vias = 0, pref = 0, non_pref = 0;

        for (size_t i = 1; i < path.size(); i++) {
            auto [cl, cx, cy] = path[i];            // current 
            auto [pl, px, py] = path[i - 1];        // previous

            if (cl != pl) vias++;
            else {
                bool vertical = (cy != py);  // if y has changed, the move is vertical
                bool m1 = (cl == 1);  // check if the current layer is M1 
                (m1 != vertical) ? pref++ : non_pref++;
            }
        }

        int total_cost = vias * VIA_COST + pref + non_pref * NON_PREF_COST;

        cout << "════════════════════════════════════════════\n";
        cout << "Net: " << net_id << "\n";
        cout << "Vias: " << vias << " | ";
        cout << "Preferred: " << pref << " | ";
        cout << "Non-pref: " << non_pref << "\n";
        cout << "Total cost: " << total_cost << "\n";
        cout << "════════════════════════════════════════════\n";
    }
}


void writeOutput(const string& filename) {
    int i = filename.find('_'), j = filename.rfind('.');
    string filepath = "../Tests/output_" + filename.substr(i + 1, j - i - 1) + ".txt";
    ofstream out(filepath);

    for (const auto& [net_id, path] : routed_paths) {
        out << "net" << net_id;
        for (const auto& cell : path) {
            out << " (" << get<0>(cell) << ", " << get<1>(cell) << ", " << get<2>(cell) << ")";
        }
        out << endl;
    }
}
