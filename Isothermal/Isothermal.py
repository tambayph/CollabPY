import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.image as mpimg  # Import the image module
import requests
from matplotlib.patheffects import withStroke
from scipy.interpolate import Rbf
import geopandas as gpd
import os
import sys
from datetime import datetime, timedelta
###################################################################################################

try:
    date = sys.argv[1]
except IndexError:
    # Calculate the date of yesterday
    date = datetime.now() - timedelta(days=1)
    # Format the date as YYYYMMDD
    date = date.strftime("%Y%m%d")

folder = os.path.dirname(os.path.abspath(__file__))

###################################################################################################

# Replace 'your_api_url_here' with the actual API URL that provides the JSON data.
api_url = f'http://10.11.1.107/api/temperature/maximum/{date}'

# Send a GET request to the API
response = requests.get(api_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()

    # Create an empty list to hold the data
    data_list = []

    # Iterate through the data and extract the required information
    for station in data:
        stn_number = station["stationNumber"]
        stn_name = station['station']["stn_name"]
        lat = station['station']["lat"]
        lon = station['station']["lon"]
        total_value = station["value"]

        # Append a new row to the data list
        data_list.append({"#": stn_number, "Name": stn_name,
                         "lat": lat, "lon": lon, "Temp": total_value})

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)

    # Save the DataFrame to a CSV file
    df.to_excel(f'{folder}/output.xlsx', index=False)

# Load your CSV data
temp_obs = pd.read_excel(f'{folder}/output.xlsx')
philippines = gpd.read_file(f'{folder}/Resources/Provinces.shp')

# Replace 'T' with '0' in the 'Temp' column
temp_obs['Temp'] = temp_obs['Temp'].replace('T', '0')

# Convert the 'Temp' column to numeric (assuming it contains numbers)
temp_obs['Temp'] = pd.to_numeric(temp_obs['Temp'])
temp_obsog = temp_obs['Temp']

# Rearrange the DataFrame based on the 'Temp' column in descending order
temp_obs = temp_obs.sort_values(by='Temp', ascending=False)

# Reset the index of the DataFrame if needed
temp_obs_sorted = temp_obs.reset_index(drop=True)

# Extract the latitude, longitude, and rainfall values
lon = temp_obs['lon'].astype(float)
lat = temp_obs['lat'].astype(float)
obs_temp = temp_obs['Temp'].astype(float)

# Create a grid of coordinates for interpolation
grid_lon = np.linspace(114, 127, 500)
grid_lat = np.linspace(21, 5, 500)
grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat, sparse=False)

# Perform RBF interpolation on the grid
# You can choose the desired RBF function
rbf = Rbf(lon, lat, obs_temp, function='linear')
grid_temp = rbf(grid_lon, grid_lat)

# Create a GeoDataFrame for the interpolated data
interpolated_data = pd.DataFrame({
    'Longitude': grid_lon.flatten(),
    'Latitude': grid_lat.flatten(),
    'Interpolated_Rainfall': grid_temp.flatten()
})
interpolated_gdf = gpd.GeoDataFrame(
    interpolated_data,
    geometry=gpd.points_from_xy(
        interpolated_data.Longitude, interpolated_data.Latitude)
)

# Perform a spatial join to mask the interpolated data to the shapefile
interpolated_data_with_shapefile = gpd.sjoin(
    interpolated_gdf, philippines, how='inner', op='intersects')

# Color scheme of the rainfall data with RGB values as floats
rgb = [
    [0.0, 0.772, 1.0],      # Light Blue
    [0.0, 1.0, 0.0],        # Green
    [1.0, 1.0, 0.0],        # Yellow
    [1.0, 0.667, 0.0],      # Orange
    [1.0, 0.0, 0.0],        # Red
    
    # [0.518, 0.0, 0.659]     # Purple
]

cmap = ListedColormap(rgb)
boundaries = [5, 10, 20, 28, 33, 40]
norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_axis_off()

# Plot the shapefile
philippines.boundary.plot(ax=ax, color='black', linewidth=1)

# Plot the masked interpolated data with custom colors
sc = interpolated_data_with_shapefile.plot(
    column='Interpolated_Rainfall', cmap=cmap, norm=norm, ax=ax, markersize=5)


# Legend outside the figure
divider = make_axes_locatable(ax)
cax = divider.append_axes("bottom", size="2%", pad=0)

# Custom labels for color bar ticks
tick_labels = ['T < 10',
               '10 ≤ T < 20',
               '20 ≤ T < 28',
               '28 ≤ T ≤ 33',
               'T > 33'
               ]

# Calculate positions for the tick labels in the middle of each color segment
tick_positions = [0.5 * (boundaries[i] + boundaries[i + 1])
                  for i in range(len(boundaries) - 1)]

# Create a ScalarMappable with a colormap and norm
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

# Add the color bar to the plot
cbar = plt.colorbar(sm, cax=cax, orientation="horizontal",
                    boundaries=boundaries, ticks=tick_positions)
cbar.ax.set_xticklabels(tick_labels, fontsize=8)
cbar.set_label('in °C', size=10)
cbar.ax.tick_params(size=0)

# Add a small image
# Replace 'small_image.png' with the path to your image
small_image = mpimg.imread(f'{folder}/Resources/PAGASA_Logo.png')
small_image_ax = fig.add_axes([0.13, 0.87, 0.1, 0.1])
small_image_ax.imshow(small_image)
small_image_ax.axis('off')  # Turn off axis for the small image

########################################################################################################################
# Parse the script_name as a datetime
date_obj = datetime.strptime(date, "%Y%m%d")

# Format the datetime object as "Month day, year"
formatted_date = date_obj.strftime("%B %d, %Y")

# Add text in the upper-left corner
upper_left_text = f"24-HOUR ISOTHERMAL ANALYSIS\n{formatted_date}"
fig.text(0.24, 0.91, upper_left_text, fontsize=12,
         color='black', weight='bold')

# Add text in the upper-left corner
iso = "WFS-13 Rev.0/15-08-2023"
fig.text(0.68, 0.97, iso, fontsize=10, color='black', weight='bold')

# Add text in the upper-left corner
synop = "24-HOUR HIGHEST TEMPERATURE(°C)"
fig.text(0.14, 0.83, synop, fontsize=10, color='red', weight='bold')

# Assuming your data is stored in a DataFrame named 'temp_obs_sorted'
selected_data1 = temp_obs_sorted.iloc[:5, [0]]
selected_data2 = temp_obs_sorted.iloc[:5, [1]]
selected_data3 = temp_obs_sorted.iloc[:5, [4]]

desired_width = 50
# Left-align the text in the 'Location' column
selected_data2['Name'] = selected_data2['Name'].str.ljust(desired_width)
selected_data3['Temp'] = selected_data3['Temp'].astype(str)
selected_data3['Temp'] = selected_data3['Temp'].str.ljust(desired_width)

# Print the formatted DataFrame
text_representation1 = selected_data1.to_string(header=False, index=False)
text_representation2 = selected_data2.to_string(header=False, index=False)
text_representation3 = selected_data3.to_string(header=False, index=False)

fig.text(0.14, 0.76, text_representation1,
         fontsize=8, color='red', weight='bold')
fig.text(0.19, 0.76, text_representation2,
         fontsize=8, color='red', weight='bold')
fig.text(0.45, 0.76, text_representation3,
         fontsize=8, color='red', weight='bold')

# Define the white outline effect
outline_effect = [withStroke(linewidth=3, foreground='white')]

# Annotate points with Temp values
for i, temp in enumerate(temp_obsog):
    ax.annotate(f'{temp:.1f}', (temp_obs['lon'][i], temp_obs['lat'][i]), fontsize=8, color='black',
                alpha=0.7, path_effects=outline_effect)
########################################################################################################################
# Save the figure

fig.tight_layout()
plt.savefig(f'{folder}/isotherm_images/{date}.png', bbox_inches='tight', pad_inches=0.1, dpi=1200)

transfer = os.path.join(folder, '../copytotera')
sys.path.append(transfer)

from copytotera import mount_network_server, transfer_to_nas, nas_local_dir

# Define the base remote path
nas_remote_path = 'wd.s.dstor.pagasa.local/wfs/Isothermal/'

previous_day_date = datetime.now() - timedelta(days=1)
previous_day_formatted = previous_day_date.strftime("%Y/%m %b'%y").upper()

# Mount the network server
mount_network_server(nas_remote_path, nas_local_dir)

# Transfer the source image to the NAS local directory
transfer_to_nas(f'{folder}/isotherm_images/{date}.png', f'{nas_local_dir}/{previous_day_formatted}/')
