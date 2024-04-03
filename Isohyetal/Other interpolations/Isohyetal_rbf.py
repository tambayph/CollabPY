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
from datetime import datetime

###################################################################################################

try:
    date = sys.argv[1]
except IndexError:
    date = datetime.now().strftime("%Y%m%d")

folder = os.path.dirname(os.path.abspath(__file__))
###################################################################################################

# Replace 'your_api_url_here' with the actual API URL that provides the JSON data.
api_url = f'http://10.11.1.107/api/rainfall/{date}0000'

# Send a GET request to the API
response = requests.get(api_url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()

    # Create an empty list to hold the data
    data_list = []

    # Iterate through the data and extract the required information
    for station in data:
        stn_number = station["stn_number"]
        stn_name = station["stn_name"]
        lat = station["lat"]
        lon = station["lon"]
        total_value = station["total"][0]

        # Append a new row to the data list
        data_list.append({"#": stn_number, "Name": stn_name,
                         "lat": lat, "lon": lon, "RR": total_value})

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)

    # Save the DataFrame to a CSV file
    df.to_excel(f"{folder}/output.xlsx", index=False)

# Load your CSV data
rr_obs = pd.read_excel(f'{folder}/output.xlsx')
philippines = gpd.read_file(f'{folder}/Provinces.shp')

# Replace 'T' with '0' in the 'RR' column
rr_obs['RR'] = rr_obs['RR'].replace('T', '0')

# Convert the 'RR' column to numeric (assuming it contains numbers)
rr_obs['RR'] = pd.to_numeric(rr_obs['RR'])
rr_obsog = rr_obs['RR']

# Rearrange the DataFrame based on the 'RR' column in descending order
rr_obs = rr_obs.sort_values(by='RR', ascending=False)

# Reset the index of the DataFrame if needed
rr_obs_sorted = rr_obs.reset_index(drop=True)

# Extract the latitude, longitude, and rainfall values
lon = rr_obs['lon'].astype(float)
lat = rr_obs['lat'].astype(float)
obs_rr = rr_obs['RR'].astype(float)

# Create a grid of coordinates for interpolation
grid_lon = np.linspace(114, 127, 500)
grid_lat = np.linspace(21, 5, 500)
grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat, sparse=False)

# Perform RBF interpolation on the grid
# You can choose the desired RBF function
rbf = Rbf(lon, lat, obs_rr, function='linear')
grid_rr = rbf(grid_lon, grid_lat)

# Create a GeoDataFrame for the interpolated data
interpolated_data = pd.DataFrame({
    'Longitude': grid_lon.flatten(),
    'Latitude': grid_lat.flatten(),
    'Interpolated_Rainfall': grid_rr.flatten()
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
    [1.0, 1.0, 1.0],        # White
    [0.0, 0.772, 1.0],      # Light Blue
    [1.0, 1.0, 0.0],        # Yellow
    [1.0, 0.667, 0.0],      # Orange
    [1.0, 0.0, 0.0],        # Red
    [1.0, 0.451, 0.874],    # Pink
    [0.518, 0.0, 0.659]     # Purple
]

cmap = ListedColormap(rgb)
boundaries = [0, 1, 30, 60, 180, 360, 720, 5000]
norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)

# Plotting
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_axis_off()

# Plot the shapefile
philippines.boundary.plot(ax=ax, color='black', linewidth=1)

# Plot the masked interpolated data with custom colors
sc = interpolated_data_with_shapefile.plot(
    column='Interpolated_Rainfall', cmap=cmap, norm=norm, ax=ax, markersize=5)

# sc = interpolated_gdf.plot(
    #  column='Interpolated_Rainfall', cmap=cmap, norm=norm, ax=ax, markersize=5)
    
# Legend outside the figure
divider = make_axes_locatable(ax)
cax = divider.append_axes("bottom", size="2%", pad=0)

# Custom labels for color bar ticks
tick_labels = ['<1.0 (Trace)',
               '30 (Very Light)',
               '60 (Light)',
               '180 (Moderate)',
               '360 (Heavy)',
               '720 (Intense)',
               '>720 (Torrential)'
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
cbar.set_label('mm', size=10)
cbar.ax.tick_params(size=0)

# Add a small image
# Replace 'small_image.png' with the path to your image
small_image = mpimg.imread(f'{folder}/PAGASA_Logo.png')
small_image_ax = fig.add_axes([0.13, 0.87, 0.1, 0.1])
small_image_ax.imshow(small_image)
small_image_ax.axis('off')  # Turn off axis for the small image

########################################################################################################################
# Parse the script_name as a datetime
date_obj = datetime.strptime(date, "%Y%m%d")

# Format the datetime object as "Month day, year"
formatted_date = date_obj.strftime("%B %d, %Y")

# Add text in the upper-left corner
upper_left_text = f"24-HOUR ISOHYETAL ANALYSIS\n{formatted_date}"
fig.text(0.24, 0.91, upper_left_text, fontsize=12,
         color='black', weight='bold')

# Add text in the upper-left corner
iso = "WFS-13 Rev.1/15-01-2024"
fig.text(0.68, 0.97, iso, fontsize=10, color='black', weight='bold')

# Add text in the upper-left corner
synop = "24-HOUR HIGHEST RAINFALL(mm)"
fig.text(0.14, 0.83, synop, fontsize=10, color='blue', weight='bold')

# Assuming your data is stored in a DataFrame named 'rr_obs_sorted'
selected_data1 = rr_obs_sorted.iloc[:5, [0]]
selected_data2 = rr_obs_sorted.iloc[:5, [1]]
selected_data3 = rr_obs_sorted.iloc[:5, [4]]

desired_width = 30
# Left-align the text in the 'Location' column
selected_data2['Name'] = selected_data2['Name'].str.ljust(desired_width)
selected_data3['RR'] = selected_data3['RR'].astype(str)
selected_data3['RR'] = selected_data3['RR'].str.ljust(desired_width)

# Print the formatted DataFrame
text_representation1 = selected_data1.to_string(header=False, index=False)
text_representation2 = selected_data2.to_string(header=False, index=False)
text_representation3 = selected_data3.to_string(header=False, index=False)

fig.text(0.14, 0.76, text_representation1,
         fontsize=8, color='blue', weight='bold')
fig.text(0.19, 0.76, text_representation2,
         fontsize=8, color='blue', weight='bold')
fig.text(0.41, 0.76, text_representation3,
         fontsize=8, color='blue', weight='bold')

# Define the white outline effect
outline_effect = [withStroke(linewidth=3, foreground='white')]

# Annotate points with RR values
for i, rr in enumerate(rr_obsog):
    ax.annotate(f'{rr:.1f}', (rr_obs['lon'][i], rr_obs['lat'][i]), fontsize=8, color='black',
                alpha=0.7, path_effects=outline_effect)
########################################################################################################################
# Save the figure

fig.tight_layout()
plt.savefig(f'{folder}/isohyet_images/{date}rbf.png', bbox_inches='tight', pad_inches=0.1, dpi=1200)
plt.show()
