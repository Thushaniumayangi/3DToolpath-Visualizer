import numpy as np
import matplotlib.pyplot as plt

# Sample Data (replace this with actual toolpath_data[30] from your parsed file)
# For now, hardcoded coordinates just for testing — replace these
toolpath_layer_30 = [
    [(-10659, -14881), (-10677, -15291), (-10757, -15291)],
    [(-10660, -13060), (-10715, -12491), (-10837, -15291)],
    [(-10917, -15291), (-10795, -12491), (-10875, -12491)]
]

def generate_heatmap(layer_data, grid_size=300, Q=1.0, sigma=0.5):
    points = [(x / 1000, y / 1000) for segment in layer_data for (x, y) in segment]
    xs, ys = zip(*points)
    x_min, x_max = min(xs) - 1, max(xs) + 1
    y_min, y_max = min(ys) - 1, max(ys) + 1
    x = np.linspace(x_min, x_max, grid_size)
    y = np.linspace(y_min, y_max, grid_size)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    for x0, y0 in points:
        Z += Q * np.exp(-((X - x0)**2 + (Y - y0)**2) / (2 * sigma**2))
    return X, Y, Z

def plot_toolpath_and_heatmap(layer_data):
    X, Y, Z = generate_heatmap(layer_data)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.contourf(X, Y, Z, levels=50, cmap='hot')
    for segment in layer_data:
        x_vals = [x / 1000 for x, y in segment]
        y_vals = [y / 1000 for x, y in segment]
        ax.plot(x_vals, y_vals, color='cyan', marker='o')
    ax.set_title("Layer 30: Tool Path with Heat Overlay")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.axis("equal")
    plt.show()

# Call the function
plot_toolpath_and_heatmap(toolpath_layer_30)
