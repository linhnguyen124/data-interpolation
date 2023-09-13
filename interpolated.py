import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import NearestNDInterpolator
import matplotlib.pyplot as plt

# Function to read contour points and gain values from a GXT file
def read_contour_points(file_path):
    contour_points = []
    gain_values = []
    with open(file_path, 'r') as file:
        reading_points = False
        gain = None
        for line in file:
            line = line.strip()
            if line.startswith("P"):
                coords = line.split('=')[1].split(';')
                latitude = float(coords[1])
                longitude = float(coords[0])
                # Translate points with longitude < 0 to the corresponding points on the opposite side
                if longitude < 0:
                    longitude += 360
                contour_points.append([longitude, latitude])
                if gain is not None:
                    gain_values.append(gain)
            elif line.startswith("gain="):
                gain = float(line.split('=')[1])
    return np.array(contour_points), np.array(gain_values)

# Read contour points and gain values from the GXT file
contour_points, gain_values = read_contour_points('prepared.gxt')

# Create a Delaunay triangulation
triangulation = Delaunay(contour_points)

# Define a grid for interpolation (can adjust the density)
x_grid, y_grid = np.meshgrid(np.linspace(contour_points[:, 0].min(), contour_points[:, 0].max(), 400),
                             np.linspace(contour_points[:, 1].min(), contour_points[:, 1].max(), 400))

# Create an interpolator using nearest-neighbor interpolation
interp = NearestNDInterpolator(triangulation, gain_values)

# Evaluate the interpolator on the grid
gain_grid = interp(x_grid, y_grid)

# Define the number of color levels (discrete colors) in the color map
num_levels = 20

# Create a scatter plot of the original contour points with color based on gain
plt.scatter(contour_points[:, 0], contour_points[:, 1], c=gain_values, cmap='coolwarm', s=10, label='Contour Points', zorder=2)

# Create a contour plot of the interpolated gain values with specified color levels
contour = plt.contourf(x_grid, y_grid, gain_grid, cmap='coolwarm', zorder=1, levels=num_levels)

# Add color bar with specified number of ticks
cbar = plt.colorbar(contour, label='Gain Values (dB)', ticks=np.linspace(gain_values.min(), gain_values.max(), num_levels))

# Customize the plot
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Nearest-Neighbor Interpolation of Contour Points with Gain Color')
plt.legend()

# Show the plot
plt.show()
