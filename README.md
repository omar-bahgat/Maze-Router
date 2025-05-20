# Maze-Router

This project implements a **2-layer maze router** based on Lee's algorithm for connecting nets across a routing grid. It supports routing with **cost-aware pathfinding**, using two metal layers and accounts for **obstacles**, **vias**, and **non-preferred direction penalties**.

## Implemenation

### Overview

The maze router operates on a N x M grid with two layers:

- Layer M1: Optimized for horizontal routing.
- Layer M2: Optimized for vertical routing.

---

### Key Features

- Multi-pin net routing with support for arbitrary pin counts
- Cost-aware routing using Lee’s algorithm with:
  - Preferred vs. non-preferred direction costs
  - Via penalties when switching layers
  - Obstacle handling
- Output summary with routing statistics:
  - Total cost
  - Via, preferred, and non-preferred segment counts
- Modular design with configurable cost parameters

---

### Algorithm

Routing is performed using a **modified Lee's algorithm** with Dijkstra-like cost propagation:

1. **Flood-fill** from the source pin to the destination using a priority queue.
2. At each step, consider:
   - Preferred direction moves (low cost)
   - Non-preferred moves (penalized)
   - Via transitions between M1 and M2 (penalized)
3. **Obstacles** are avoided entirely.
4. Paths are reconstructed from backtracking pointers.

Routing is done **segment-by-segment** for each net by connecting sequential pin pairs.

---

### Bonus: Net Reordering Heuristic

**Net reordering feature** is included to improve routing success and cost by prioritizing more "difficult" nets first.

The priority is based on a weighted sum of:

- Estimated route cost
- Manhattan distance
- Pin count

Enable this by setting:

```cpp
ENABLE_NET_REORDERING = true;
```

### Assumptions

- The input file must start with grid size and costs: `rows, cols, via_cost, non_pref_cost`.
- Obstacle lines begin with `OBS` and must have valid layer (1 or 2) and coordinates within grid bounds.
- Net lines start with `net` followed by a net ID and at least two pin coordinates in `(layer, x, y)` format.
- Layers are always 1 (M1) or 2 (M2); coordinates must be within grid dimensions.
- Pins cannot overlap with obstacles.
- The input format must be strictly followed; any invalid line or format causes the program to exit with an error.

### Limitations

- Only supports two layers (M1 and M2).
- Fixed grid size with static obstacles.
- Uniform cost penalties for vias and non-preferred moves.
- Nets routed sequentially between pins.
- No error handling for invalid input files.

## Input Format

The input to the router is a text file that specifies the size of the grid, via cost, non-preferred direction cost, the obstacles, and the nets to be routed.

### The input format follows the structure:

1. **Grid size and costs**: The first line specifies the size of the grid, the via cost, and the non-preferred direction cost in the format `rows, cols, via_cost, non_pref_cost`
   Example:

   ```
   6, 6, 4, 10
   ```

2. **Obstacles**: Each obstacle is specified with the keyword `OBS`, followed by the coordinates in the format `(layer, x, y)`.
   Example:

   ```
   OBS (1, 33, 44)
   OBS (2, 55, 77)
   ```

3. **Nets**: Each net is defined with the net name followed by pairs of coordinates for each pin. Each pin is specified as `(pin_layer, pin_x, pin_y)` where `pin_layer` is either 1 (for layer 1) or 2 (for layer 2).  
   Example:
   ```
   net1 (1, 10, 20) (2, 30, 50) (1, 5, 100)
   net2 (2, 100, 200) (1, 300, 50)
   net3 (1, 100, 50) (2, 300, 150) (2, 50, 50) (1, 2, 2)
   .
   .
   ```

### Input Example:

```
6, 6, 4, 10
OBS (1, 1, 5)
net1 (1, 0, 5) (2, 5, 4)
net2 (1, 0, 0) (1, 3, 5)
```

## Output Format

The output from the router is a text file that lists the cells used by each net. Each line of this file follows the format:

```
Net_name (cell_1_layer, cell_1_x, cell_1_y) (cell_2_layer, cell_2_x, cell_2_y) ...
```

The cells represent the complete path taken by each net, starting from a pin and connecting to all other pins.

### Example Output:

```
net1 (1, 10, 20) (1, 11, 20) (1, 12, 20) ...
net2 (2, 100, 200) (2, 100, 201) (2, 100, 202) ...
```

## How to Use

Follow these steps to build and run the maze router:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/omar-bahgat/Maze-Router
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd Maze-Router
   ```

3. **Build and Run the Router**
   ```bash
   cd src
   make
   ./router
   ```

# Visualizer

This Python script provides a simple visualization tool for routing results in grid-based routing problems. It displays a grid layout with obstacles, pins, and the routing paths between them.

## Features

- Parses input file with:
  - Grid dimensions
  - Obstacle positions (across layers)
  - Net pin positions (across layers)
- Parses output file with:
  - Routed cell paths for each net
- Visualizes:
  - Grid layout on one or more layers
  - Obstacles in black
  - Pins (input/output) in green
  - Routes in unique colors per net
  - Vias (layer transitions) in red
- Interactive zoom, pan, and reset functionality

## Requirements

- Python 3.x

  - `matplotlib`

- Install required packages:

  ```bash
  pip install matplotlib
  ```

## Usage

- Edit the visualize.py file and modify the following lines at the bottom to point to your input/output files:

  ```
  input_file = r"tests/<input_file_name>.txt"
  ```

  ```
  output_file = r"tests/<output_file_name>.txt"
  ```

- Then run the script:
  ```
   python visualize.py
  ```
- Each layer is visualized in a separate subplot
- Input pins are shown in light green
- Output pins are shown in darker green
- Vias (connections between layers) are shown in red
- Zoom and pan supported via mouse interaction
- "Reset View" button restores the default zoom level
