import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as patches
import re
from matplotlib.widgets import Button
matplotlib.use('Qt5Agg')

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
    obstacles = [tuple(map(int, re.search(r'\((\d+),\s*(\d+),\s*(\d+)\)', l).groups())) for l in obs_lines]

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

    #fig, axs = plt.subplots(1, len(all_layers), figsize=(12 * len(all_layers), 12), dpi=150)
    fig, axs = plt.subplots(1, len(all_layers), figsize=(8 * len(all_layers), 8), layout="constrained")

    if len(all_layers) == 1:
        axs = [axs]
    layer_to_ax = dict(zip(all_layers, axs))

    layer_artists = {layer: [] for layer in all_layers}

    def draw_grid(ax):
        ax.grid(False)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        step = max(1, int(min(x_range, y_range) // 20))
        ax.set_xticks(range(int(xlim[0]), int(xlim[1]) + 1, step))
        ax.set_yticks(range(int(ylim[0]), int(ylim[1]) + 1, step))
        ax.grid(True, linestyle=':', linewidth=0.8)

    for layer, ax in layer_to_ax.items():
        ax.set_title(f"Layer {layer}")
        ax.set_aspect('equal')
        ax.set_facecolor('#f0f0f0')
        ax.add_patch(patches.Rectangle(
            (0, 0), grid_width, grid_height,
            edgecolor='black', facecolor='white', linewidth=2, zorder=0
        ))
        ax.set_xlim(-1, grid_width + 1)
        ax.set_ylim(-1, grid_height + 1)
        draw_grid(ax)

    for (layer, ox, oy) in obstacles:
        ax = layer_to_ax.get(layer)
        if ax:
            r = patches.Rectangle((ox, oy), 1, 1, color='black', zorder=1)
            ax.add_patch(r)
            layer_artists[layer].append(r)

    for net_idx, net in enumerate(output_nets):
        color = cmap(net_idx)
        net_label = net_names[net_idx] if net_names else f"net{net_idx+1}"
        layers_labeled = set()
        for (layer, x, y) in net:
            ax = layer_to_ax[layer]
            label = net_label if (net_label, layer) not in layers_labeled else None
            r = patches.Rectangle((x, y), 1, 1, color=color, zorder=1, label=label)
            ax.add_patch(r)
            layer_artists[layer].append(r)
            layers_labeled.add((net_label, layer))

    used_via_layers = set()
    for net_idx, net in enumerate(output_nets):
        net_color = cmap(net_idx)
        for i in range(len(net) - 1):
            l1, x1, y1 = net[i]
            l2, x2, y2 = net[i + 1]
            if l1 != l2:
                for l in [l1, l2]:
                    ax = layer_to_ax.get(l)
                    if ax:
                        label = "Via" if l not in used_via_layers else None
                        r = patches.Rectangle((x2 + 0.27, y2 + 0.27), 0.45, 0.45,
                                              linewidth=1.2, edgecolor='black',
                                              facecolor='red', zorder=6, label=label)
                        ax.add_patch(r)
                        layer_artists[l].append(r)
                        if label:
                            used_via_layers.add(l)

    used_light_pin_labels_per_layer = set()
    used_other_pin_labels_per_layer = set()
    for net_idx, net in enumerate(input_nets):
        for i, (layer, x, y) in enumerate(net):
            ax = layer_to_ax.get(layer)
            if ax:
                if i == 0:
                    label_key = (layer, "Input Pin")
                    label = "Input Pin" if label_key not in used_light_pin_labels_per_layer else None
                    r = patches.Rectangle((x + 0.15, y + 0.15), 0.7, 0.7,
                                          linewidth=1, edgecolor='black',
                                          facecolor='#90ee90', zorder=4, label=label)
                    ax.add_patch(r)
                    layer_artists[layer].append(r)
                    used_light_pin_labels_per_layer.add(label_key)
                else:
                    label_key = (layer, "Output Pin")
                    label = "Output Pin" if label_key not in used_other_pin_labels_per_layer else None
                    r = patches.Rectangle((x + 0.15, y + 0.15), 0.7, 0.7,
                                          linewidth=1, edgecolor='black',
                                          facecolor='green', zorder=4, label=label)
                    ax.add_patch(r)
                    layer_artists[layer].append(r)
                    used_other_pin_labels_per_layer.add(label_key)

    def set_initial_limits():
        for ax_ in axs:
            ax_.set_xlim(-1, grid_width + 1)
            ax_.set_ylim(-1, grid_height + 1)
            draw_grid(ax_)
            ax_.figure.canvas.draw_idle()

    def draw_grid(ax):
        ax.grid(False)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        step = max(1, int(min(x_range, y_range) // 20))
        ax.set_xticks(range(int(xlim[0]), int(xlim[1]) + 1, step))
        ax.set_yticks(range(int(ylim[0]), int(ylim[1]) + 1, step))
        ax.grid(True, linestyle=':', linewidth=0.8)

    for ax in axs:
        set_initial_limits()
        draw_grid(ax)

    def on_scroll(event):
        base_scale = 1.2
        if event.xdata is None or event.ydata is None:
            return
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale
        for ax in axs:
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            xdata = event.xdata
            ydata = event.ydata
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
            relx = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
            rely = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])
            ax.set_xlim([xdata - new_width * relx, xdata + new_width * (1 - relx)])
            ax.set_ylim([ydata - new_height * rely, ydata + new_height * (1 - rely)])
            draw_grid(ax)
        fig.canvas.draw_idle()

    def on_press(event):
        for ax in axs:
            ax._pan_start = (event.x, event.y, ax.get_xlim(), ax.get_ylim())

    def on_motion(event):
        if event.x is None or event.y is None:
            return
        for ax in axs:
            if not hasattr(ax, '_pan_start') or ax._pan_start is None:
                continue
            x_press, y_press, xlim, ylim = ax._pan_start
            dx = event.x - x_press
            dy = event.y - y_press
            scale_x = (xlim[1] - xlim[0]) / ax.bbox.width
            scale_y = (ylim[1] - ylim[0]) / ax.bbox.height
            ax.set_xlim(xlim[0] - dx * scale_x, xlim[1] - dx * scale_x)
            ax.set_ylim(ylim[0] - dy * scale_y, ylim[1] - dy * scale_y)
            draw_grid(ax)
        fig.canvas.draw_idle()
    def on_reset(event):
        set_initial_limits()
        

    def on_release(event):
        for ax in axs:
            ax._pan_start = None
    reset_ax = plt.axes([0.45, 0.01, 0.1, 0.04])  # x, y, width, height in figure coords
    reset_button = Button(reset_ax, 'Reset View', hovercolor='0.975')
    # Connect only zoom and pan
    reset_button.on_clicked(on_reset)
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    fig.canvas.mpl_connect('button_release_event', on_release)
    
    # Legend
    handles, labels = axs[0].get_legend_handles_labels()
    legend_handles = {}
    for h, l in zip(handles, labels):
        if l not in legend_handles:
            legend_handles[l] = h
    #fig.legend(legend_handles.values(), legend_handles.keys(), loc='center right', fontsize='small', borderaxespad=0.1)
    fig.legend(legend_handles.values(), legend_handles.keys(), loc='upper right', fontsize='small', bbox_to_anchor=(1.0, 1.0),borderaxespad=0.1)


    fig.tight_layout(rect=[0, 0.1, 1, 0.95])
    plt.show()

            

if __name__ == "__main__":
    input_file = r"tests/input_5x5_1.txt"
    output_file = r"tests/output_5x5_1.txt"
    # input_file = r"tests_2\input_5x5_2.txt"
    # output_file = r"tests_2\output_5x5_2.txt"
    grid_size, obstacles, input_nets, net_names = parse_input_file(input_file)
    output_nets = parse_output_file(output_file)
    visualize(grid_size, obstacles, input_nets, output_nets, net_names)