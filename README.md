# Maze-Router

## Input File Format
  ```
  <Grid_Size_x>,<Grid_Size_y>,<Via_Cost>,<Non_Prefered_Cost>
  OBS (<layer>, <x>, <y>)
  net<number> (<layer>, <x>, <y>) (<layer>, <x>, <y>)
  ```
## Output File Format
  ```
  net<number> (<layer>, <x>, <y>) (<layer>, <x>, <y>)
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
##  Usage
- Edit the visualize_2.py file and modify the following lines at the bottom to point to your input/output files:
  - input_file = r"tests/<input_file_name>.txt"
  - output_file = r"tests/<output_file_name>.txt"
- Then run the script:
  - python visualize_2.py
- Each layer is visualized in a separate subplot
- Input pins are shown in light green
- Output pins are shown in darker green
- Vias (connections between layers) are shown in red
- Zoom and pan supported via mouse interaction
- "Reset View" button restores the default zoom level
