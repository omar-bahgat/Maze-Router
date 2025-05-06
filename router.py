import re
from collections import deque

# global variables
obstacles = []
nets = {}
routed_nets = {}
ROWS = COLS = VIA_COST = NON_PREF_COST = 0

def parse_input_file(file_path):
    
    with open(file_path) as f:
        global ROWS, COLS, VIA_COST, NON_PREF_COST
        values = f.readline().strip()
        ROWS, COLS, VIA_COST, NON_PREF_COST = map(int, values.split(','))

        for line in f:
            line = line.strip()
            if line.startswith("OBS"):
                obstacles.append(tuple(map(int, re.findall(r"\d+", line))))
            elif line.startswith("net"):
                net_name, coords = line.split(' ', 1)
                nets[net_name] = [tuple(map(int, re.findall(r"\d+", coord))) for coord in coords.split(') (')]

def print_input_file_info():
    print(f"Rows: {ROWS}\nCols: {COLS}\nVia Cost: {VIA_COST}\nNon-preferred Direction Cost: {NON_PREF_COST}\n")


def floodfill(start, end, visited_global, allowed_start):
    
    queue = deque([(start[0], start[1], start[2])])  # (layer, x, y)

    grid = {
        1: [[float('inf')] * COLS for _ in range(ROWS)],
        2: [[float('inf')] * COLS for _ in range(ROWS)]
    }
    grid[start[0]][start[1]][start[2]] = 0

    parent = {}
    visited_local = set()

    while queue:
        layer, x, y = queue.popleft()

        # skip if already visited in this flood
        if (layer, x, y) in visited_local:
            continue
        visited_local.add((layer, x, y))

        # skip if globally blocked and not the allowed start
        if (layer, x, y) in visited_global and (allowed_start is None or (layer, x, y) != allowed_start):
            continue
        if (x, y) in obstacles:
            continue

        current_cost = grid[layer][x][y]

        # reached end
        if (x, y) == (end[1], end[2]):
            if layer != end[0]:
                if grid[end[0]][x][y] > current_cost + VIA_COST:
                    grid[end[0]][x][y] = current_cost + VIA_COST
                    parent[(end[0], x, y)] = (layer, x, y)
                    queue.append((end[0], x, y))
                continue
                
            # reconstruct path
            path = [(layer, x, y)]
            while (layer, x, y) in parent:
                layer, x, y = parent[(layer, x, y)]
                path.append((layer, x, y))
            path.reverse()
            return grid[end[0]][end[1]][end[2]], path

        # Move in preferred directions
        if layer == 1:  # M1 = horizontal
            for dx, dy in [(0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS and (layer, nx, ny) not in visited_global and (nx, ny) not in obstacles:
                    if grid[layer][nx][ny] > current_cost + 1:
                        grid[layer][nx][ny] = current_cost + 1
                        parent[(layer, nx, ny)] = (layer, x, y)
                        queue.append((layer, nx, ny))

            # Switch to M2
            if grid[2][x][y] > current_cost + VIA_COST:
                grid[2][x][y] = current_cost + VIA_COST
                parent[(2, x, y)] = (1, x, y)
                queue.append((2, x, y))

        elif layer == 2:  # M2 = vertical
            for dx, dy in [(1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS and (layer, nx, ny) not in visited_global and (nx, ny) not in obstacles:
                    if grid[layer][nx][ny] > current_cost + 1:
                        grid[layer][nx][ny] = current_cost + 1
                        parent[(layer, nx, ny)] = (layer, x, y)
                        queue.append((layer, nx, ny))

            # Switch to M1
            if grid[1][x][y] > current_cost + VIA_COST:
                grid[1][x][y] = current_cost + VIA_COST
                parent[(1, x, y)] = (2, x, y)
                queue.append((1, x, y))

    return -1, []  # No path found

def route_nets():
    global routed_nets 

    visited_global = set()

    for net_name, coords in nets.items():
        print(f"\033[1mNet: `{net_name}`\033[0m")
        print("-" * 50)

        prev_end = None
        routed_nets[net_name] = []

        for i in range(len(coords) - 1):
            start = coords[i]
            end = coords[i + 1]
            print(f"Routing from Pin {i + 1} ({start[0]}, {start[1]}, {start[2]}), to Pin {i + 2} ({end[0]}, {end[1]}, {end[2]})\n")

            allowed_start = prev_end if prev_end == start else None
            cost, path = floodfill(start, end, visited_global, allowed_start)

            if cost == -1:
                print(f"  No route found for {net_name} from {start} to {end}")
                continue

            print("  Route:", " ".join(f"({layer}, {x}, {y})" for layer, x, y in path))
            print(f"  Cost: {cost}")
            if i < len(coords) - 2:
                print("\n******\n")
            else:
                print()

            for cell in path:
                visited_global.add(cell)

            prev_end = path[-1]
            routed_nets[net_name].append(path)

def write_output(output_file_path):
    with open(output_file_path, "w") as f:
        for net_name, paths in routed_nets.items():
            full_path = []
            for i, segment in enumerate(paths):
                if i == 0:
                    full_path.extend(segment)
                else:
                    # Avoid duplicating the start point if it's the same as the end of the previous path
                    if segment[0] == full_path[-1]:
                        full_path.extend(segment[1:])
                    else:
                        full_path.extend(segment)

            path_str = " ".join(f"({layer}, {x}, {y})" for (layer, x, y) in full_path)
            f.write(f"{net_name} {path_str}\n")

def main():
    
    input_file = input("Enter input filename: ").strip()
    input_file_path = f"tests/{input_file}"

    parse_input_file(input_file_path)
    print_input_file_info()

    route_nets()

    base_name = input_file.split('input')[-1]  
    output_file_path = f"tests/output{base_name}"

    write_output(output_file_path)  

if __name__ == "__main__":
    main()