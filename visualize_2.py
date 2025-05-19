import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re

def parse_input_file(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    grid_line = lines[0]
    grid_width, grid_height, *_ = map(int, grid_line.split(','))
    obs_lines, pin_lines = [], []
    for line in lines[1:]:
        if line.startswith("OBS"):
            obs_lines.append(line)
        else:
            pin_lines.append(line)
    obstacles = [tuple(map(int, re.search(r'\((\d+),\s*(\d+)\)', l).groups())) for l in obs_lines]
    pins, net_names = [], []
    for line in pin_lines:
        tokens = line.split()
        net_names.append(tokens[0])
        coords = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
        pins.append([tuple(map(int, c)) for c in coords])
    return (grid_width, grid_height), obstacles, pins, net_names

def parse_output_file(filename):
    output_nets = []
    with open(filename, 'r') as f:
        for line in f:
            coords = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            output_nets.append([tuple(map(int, c)) for c in coords])
    return output_nets

def visualize(grid_size, obstacles, input_nets, output_nets, net_names=None):
    grid_width, grid_height = grid_size
    all_layers = sorted(set(p[0] for net in output_nets for p in net))
    cmap = plt.colormaps.get_cmap('tab20')
    fig, axs = plt.subplots(1, len(all_layers), figsize=(6 * len(all_layers), 6))

    if len(all_layers) == 1:
        axs = [axs]
    layer_to_ax = dict(zip(all_layers, axs))

    for ax, layer in zip(axs, all_layers):
        ax.set_title(f"Layer {layer}")
        ax.set_xlim(-1, grid_width + 1)
        ax.set_ylim(-1, grid_height + 1)
        ax.set_aspect('equal')
        ax.set_xticks(range(grid_width))
        ax.set_yticks(range(grid_height))
        ax.grid(True, linestyle=':', linewidth=0.8)
        ax.set_facecolor('#f0f0f0')
        ax.add_patch(patches.Rectangle(
            (0, 0), grid_width, grid_height,
            edgecolor='black', facecolor='white', linewidth=2, zorder=0
        ))
    for (ox, oy) in obstacles:
        for ax in axs:
            ax.add_patch(patches.Rectangle(
                (ox, oy), 1, 1,
                color='black', label='Obstacle', zorder=1
            ))

    used_labels = set()
    for net_idx, net in enumerate(output_nets):
        color = cmap(net_idx)
        label = net_names[net_idx] if net_names else f"net{net_idx+1}"
        for (layer, x, y) in net:
            ax = layer_to_ax[layer]
            key = (layer, x, y, 'route')
            if key not in used_labels:
                ax.add_patch(patches.Rectangle((x, y), 1, 1, color=color, zorder=1))
                used_labels.add(key)

    for net_idx, net in enumerate(output_nets):
        net_color = cmap(net_idx)
        for i in range(len(net) - 1):
            l1, x1, y1 = net[i]
            l2, x2, y2 = net[i + 1]
            if l1 != l2:
                for l in [l1, l2]:
                    ax = layer_to_ax.get(l)
                    if ax:
                        label = "Via" if "Via" not in used_labels else None
                        ax.add_patch(patches.Rectangle(
                            (x2 + 0.27, y2 + 0.27), 0.45, 0.45,
                            linewidth=1.2,
                            edgecolor='black',
                            facecolor='red',
                            zorder=6,
                            label=label
                        ))
                        used_labels.add("Via")
    for net_idx, net in enumerate(input_nets):
        color = cmap(net_idx)
        label = f"{net_names[net_idx]} Pin" if net_names else f"Net{net_idx+1} Pin"
        for (layer, x, y) in net:
            ax = layer_to_ax.get(layer)
            if ax:
                ax.add_patch(patches.Rectangle(
                    (x + 0.15, y + 0.15), 0.7, 0.7, linewidth=1, edgecolor='black',
                    facecolor='green', zorder=4,
                    label=label if label not in used_labels else None
                ))
                used_labels.add(label)


    for ax in axs:
        ax.legend(loc='upper right', fontsize='small')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    input_file = r"tests_2/input_10x10_1.txt"
    output_file = r"tests_2/output_10x10_1.txt"
    # input_file = r"tests_2\input_5x5_2.txt"
    # output_file = r"tests_2\output_5x5_2.txt"
    grid_size, obstacles, input_nets, net_names = parse_input_file(input_file)
    output_nets = parse_output_file(output_file)
    visualize(grid_size, obstacles, input_nets, output_nets, net_names)
