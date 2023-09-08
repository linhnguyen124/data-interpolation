import numpy as np
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.transforms import Affine2D
import numpy as np
import matplotlib.pyplot as plt  # Added for visualization
from scipy.interpolate import interp1d

# Define a function to parse the GXT file
def parse_gxt(file_path):
    data = []
    with open(file_path, 'r') as file:
        current_data = None
        for line in file:
            line = line.strip()
            if line.startswith("[C"):
                if current_data:
                    if current_data['gain'] is not None and current_data['points']:
                        data.append(current_data)
                current_data = {'gain': None, 'points': []}
            elif current_data and line.startswith("P"):
                try:
                    point = line.split('=')[1].strip()
                    lon, lat = map(float, point.split(';'))
                    current_data['points'].append((lon, lat))
                except (ValueError, IndexError):
                    pass
            elif current_data and line.startswith("gain="):
                try:
                    current_data['gain'] = float(line.split('=')[1])
                except (ValueError, IndexError):
                    pass
        if current_data and current_data['gain'] is not None and current_data['points']:
            data.append(current_data)
    return data

# Read and parse the GXT file
gxt_file_path = 'prepared.gxt'
gxt_data = parse_gxt(gxt_file_path)

# Filter data for contours with gain > -11 dB and store their points
filtered_data = [contour for contour in gxt_data if contour['gain'] > -11]
all_points = [point for contour in filtered_data for point in contour['points']]

# Extract latitude and longitude points
latitude_points, longitude_points = zip(*all_points)

# Ensure common_interp has the same length as longitude_points
common_interp = np.linspace(0, 1, len(longitude_points))

# Create interpolation functions
interp_func_lon = interp1d(common_interp, longitude_points, kind='linear')
interp_func_lat = interp1d(common_interp, latitude_points, kind='linear')

# Use interpolation functions to get interpolated values
interpolated_longitude = interp_func_lon(common_interp)
interpolated_latitude = interp_func_lat(common_interp)

# for i, lat in enumerate(interpolated_latitude, start=0):
#     for long in interpolated_longitude:
#         if round(lat) == 100:
#             if interpolated_longitude[i] > 25 and interpolated_longitude[i] < 30:
#                 print("#################>>>>> interpolated_longitude", interpolated_longitude[i])

# Visualization: Plot the original points with translation
fig, ax = plt.subplots(figsize=(16, 12))

# Define the translation value for latitude in degrees
latitude_translation_degrees = 360

# Translate the latitude for points with latitude < 0
translated_latitude_points = [lat + latitude_translation_degrees if lat < 0 else lat for lat in latitude_points]

# Use nearest neighbor interpolation to connect the data points
ax.plot(longitude_points, translated_latitude_points, 'o', label='Original Points', markersize=5)
ax.plot(longitude_points, translated_latitude_points, '-', label='Interpolated Path (Nearest Neighbor)', linewidth=2)

# Get unique gain values from the data
unique_gain_values = np.unique(np.array(filtered_data[0]['gain']))

# Create a colormap for gain values
cmap = ListedColormap(['blue', 'green', 'yellow', 'orange', 'red'])  # Define your colormap colors here

# Normalize gain values for mapping to colors
norm = Normalize(vmin=min(unique_gain_values), vmax=max(unique_gain_values))

# Set labels and legend
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Apply horizontal rotation
rotation_degrees = 45
rot_transform = Affine2D().rotate_deg(rotation_degrees)
ax.transData = rot_transform + ax.transData

# Calculate rotated data points
rotated_points = rot_transform.transform(np.column_stack((longitude_points, translated_latitude_points)))

# Ensure longitude_points fall within the interpolation range
lon_min = min(longitude_points)
lon_max = max(longitude_points)
lon_min = max(lon_min, common_interp[0])
lon_max = min(lon_max, common_interp[-1])
longitude_points = np.linspace(lon_min, lon_max, len(longitude_points))

# Set limits to show only the region with points
x_padding = 80
y_padding = 80
min_lat = min(rotated_points[:, 1])
max_lat = max(rotated_points[:, 1])
ax.set_xlim(-90, 90)  # Set x-axis limits to -90 to 90 degrees for longitude
ax.set_ylim(min_lat - y_padding, max_lat + y_padding)  # Set y-axis limits to cover all latitudes

# Calculate the latitude range
min_latitude = np.min(translated_latitude_points)
max_latitude = np.max(translated_latitude_points)

# Iterate through the gain values and assign colors
# for i in range(len(unique_gain_values) - 1):
#     contour_start = unique_gain_values[i]
#     contour_end = unique_gain_values[i + 1]

#     # Filter points within the gain range
#     gain_range_mask = (filtered_data[0]['gain'] >= contour_start) & (filtered_data[0]['gain'] <= contour_end)

#     # Create filled contours using color based on the gain value
#     color = cmap(norm((contour_start + contour_end) / 2))
#     ax.contourf(
#         longitude_points,
#         translated_latitude_points,
#         levels=[contour_start, contour_end],
#         colors=[color],
#         alpha=0.7,  # Adjust the alpha for transparency
#         label=f'Gain: {contour_start}-{contour_end}'
#     )

# Set labels and legend
ax.legend()

plt.title('Original Points with Translated Latitude and Areas Filled Between Contours')

# Remove grid lines
ax.grid(True)

# Add colorbar with the specified ax argument
cbar = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=ax)
cbar.set_label('Gain')

# Save the figure as an image
# plt.savefig('graph_image.png', dpi=300, bbox_inches='tight')

# Show the plot (optional)
plt.show()
