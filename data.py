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

# Perform linear interpolation
interp_points = 1000  # Number of interpolated points

# Ensure common_interp has the same length as longitude_points
common_interp = np.linspace(0, 1, len(longitude_points))

# Create interpolation functions
interp_func_lon = interp1d(common_interp, longitude_points, kind='linear')
interp_func_lat = interp1d(common_interp, latitude_points, kind='linear')

# Use interpolation functions to get interpolated values
interpolated_longitude = interp_func_lon(common_interp)
interpolated_latitude = interp_func_lat(common_interp)

# Visualization: Plot the interpolated results
plt.figure(figsize=(10, 6))
plt.plot(longitude_points, latitude_points, 'o', label='Original Points', markersize=5)
# plt.plot(interpolated_longitude, interpolated_latitude, '-', label='Interpolated Path')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.grid(True)
plt.title('Interpolated Path')
plt.show()