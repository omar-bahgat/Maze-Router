#include "route.hpp"
#include <iostream>
#include <algorithm>
#include <fstream>
#include <unordered_set>

using namespace std;

bool ENABLE_NET_REORDERING = false;

map<int, vector<tuple<int, int, int>>> routed_paths;
vector<pair<int, vector<tuple<int, int, int>>>> routed_net_list;

int calculate_manhattan_distance(const vector<tuple<int, int, int>>& pins) {
    int maxDist = 0;
    for (size_t i = 0; i < pins.size(); i++) {
        auto [l1, x1, y1] = pins[i];
        for (size_t j = i + 1; j < pins.size(); j++) {
            auto [l2, x2, y2] = pins[j];
            int dist = abs(x1 - x2) + abs(y1 - y2);
            if (dist > maxDist) maxDist = dist;
        }
    }
    return maxDist;
}

int estimate_net_cost(const vector<tuple<int, int, int>>& pins) {
    const int penalty = 10;

    int cost = 0;
    for (size_t i = 0; i + 1 < pins.size(); i++) {
        auto [l1, x1, y1] = pins[i];
        auto [l2, x2, y2] = pins[i + 1];

        cost += abs(x1 - x2) + abs(y1 - y2);

        if (l1 != l2) {
            cost += penalty;  // via penalty
        }
        else if ((x1 != x2) && (y1 != y2)) {
            cost += penalty;  // non-pref  penalty
        }

        bool obstacle_found = false;
        int minX = min(x1, x2), maxX = max(x1, x2);
        int minY = min(y1, y2), maxY = max(y1, y2);

        for (int layer = 0; layer < 2 && !obstacle_found; layer++) {
            for (int x = minX; x <= maxX && !obstacle_found; x++) {
                for (int y = minY; y <= maxY; y++) {
                    if (grid[layer][x][y] == -1) {
                        cost += penalty;
                        obstacle_found = true;
                    }
                }
            }
        }
    }
    return cost;
}

int net_priority(const pair<int, vector<tuple<int, int, int>>>& net) {
    int est_cost = estimate_net_cost(net.second);
    int manhattan = calculate_manhattan_distance(net.second);
    int pin_count = (int)net.second.size();

    // weighted sum
    return est_cost * 3 + manhattan * 2 + pin_count;
}

vector<pair<int, vector<tuple<int, int, int>>>> reorderNets(
    const map<int, vector<tuple<int, int, int>>>& nets) {

    vector<pair<int, vector<tuple<int, int, int>>>> sorted(nets.begin(), nets.end());

    sort(sorted.begin(), sorted.end(), [](const auto& a, const auto& b) {
        return net_priority(a) > net_priority(b);
        });

    return sorted;
}

vector<tuple<int, int, int>> reconstructPath(
    const vector<vector<vector<tuple<int, int, int>>>>& prev,
    int startLayer, int startX, int startY,
    int endLayer, int endX, int endY) {

    vector<tuple<int, int, int>> path;
    int l = endLayer, x = endX, y = endY;

    tuple<int, int, int> lastAdded = { -1, -1, -1 };

    while (l != -1 && !(l == startLayer && x == startX && y == startY)) {
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

        if (curr.layer == endLayer && curr.x == endX && curr.y == endY) {
            return reconstructPath(prev, startLayer, startX, startY,
                curr.layer, curr.x, curr.y);
        }

        for (auto [dx, dy] : dirs) {
            int nx = curr.x + dx, ny = curr.y + dy;
            if (nx < 0 || nx >= ROWS || ny < 0 || ny >= COLS) continue;
            if (grid[curr.layer][nx][ny] == -1) continue;

            int moveCost = 1;
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

    vector<pair<int, vector<tuple<int, int, int>>>> net_list;

    if (ENABLE_NET_REORDERING) {
        net_list = reorderNets(nets);
        cout << "- Net reordering enabled.\n";
    }
    else {
        net_list.assign(nets.begin(), nets.end());
        cout << "- Net reordering disabled.\n";
    }

    routed_net_list = net_list;

    for (auto& [net_id, pins] : net_list) {
        vector<tuple<int, int, int>> full_path;

        for (size_t i = 0; i < pins.size() - 1; i++) {
            auto segment = routeNet(pins[i], pins[i + 1]);

            auto start = segment.begin();
            auto end = segment.end();

            if (i > 0 && !segment.empty() && !full_path.empty()) {
                start = segment.begin() + 1;
            }

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
    cout << "════════════════════════════════════════════\n";

    for (const auto& [net_id, _] : routed_net_list) {
        const auto& path = routed_paths[net_id];

        cout << "Net: " << "net" << net_id << "\n";

        if (path.empty()) {
            cout << "No route found\n";
            cout << "════════════════════════════════════════════\n";
            continue;
        }

        int vias = 0, pref = 0, non_pref = 0;
        for (size_t i = 1; i < path.size(); i++) {
            auto [cl, cx, cy] = path[i];
            auto [pl, px, py] = path[i - 1];
            if (cl != pl) vias++;
            else {
                bool vertical = (cy != py);
                bool m1 = (cl == 1);
                (m1 != vertical) ? pref++ : non_pref++;
            }
        }

        int total_cost = vias * VIA_COST + pref + non_pref * NON_PREF_COST;

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

    for (const auto& [net_id, _] : routed_net_list) {
        const auto& path = routed_paths[net_id];
        out << "net" << net_id;
        for (const auto& cell : path) {
            out << " (" << get<0>(cell) << ", " << get<1>(cell) << ", " << get<2>(cell) << ")";
        }
        out << endl;
    }
}
