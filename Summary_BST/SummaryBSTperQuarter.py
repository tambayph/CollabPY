from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import glob
import sys

year = sys.argv[1]
quarter = sys.argv[2]
folder = os.path.dirname(os.path.abspath(__file__))
transfer = os.path.join(folder, '../copytotera')
sys.path.append(transfer)

from copytotera import mount_network_server, transfer_to_nas, nas_local_dir
nas_remote_path = 'wd.s.dstor.pagasa.local/wfs'
# Mount the network server
mount_network_server(nas_remote_path, nas_local_dir)

# Read the PAR data from CSV
par = pd.read_csv(f'{folder}/Resources/PAR.csv', sep=',')

folder_path = f'{nas_local_dir}/Tropical Cyclone/Tropical Cyclone Best Track Data/PH{year}BST/{quarter}'
file_pattern = '*.txt'

# Get a list of all text files in the folder
files = glob.glob(os.path.join(folder_path, file_pattern))

# Create an empty dictionary to store the DataFrames
data_frames = {}

# Loop through each file and read it into a DataFrame
for file in files:
    file_name = os.path.splitext(os.path.basename(file))[0]  # Extract file name without extension
    df = pd.read_csv(file, sep='\s+', names=['col1', 'lat', 'lon', 'col4', 'col5', 'col6'], skiprows=1)
    data_frames[file_name] = df

# Create a list of DataFrames
data_frames_list = list(data_frames.values())

# Loop through the list and add the 'Your_Annotation_Column' to each DataFrame
for i, df in enumerate(data_frames_list):
    df['Your_Annotation_Column'] = chr(ord('A') + i)

# Create a Basemap instance with Mercator projection
m = Basemap(projection='merc', llcrnrlon=90, llcrnrlat=-0, urcrnrlon=175, urcrnrlat=45, resolution='h')
m.readshapefile(f'{folder}/Resources/Provinces', 'Provinces', linewidth=0.2, color='#343A40', zorder=3)

# Define a function to plot DataFrame on the Basemap
def plot_dataframe_with_annotation(df, color, linewidth, label, annotation_column):
    df['lat'] = df['lat'] / 10.0
    df['lon'] = df['lon'] / 10.0
    df['lat'] = df['lat'].round(1)
    df['lon'] = df['lon'].round(1)
    df['coords'] = list(zip(df['lat'], df['lon']))
    x, y = m(df['lon'].values, df['lat'].values)
    m.plot(x, y, linestyle='-', color=color, linewidth=linewidth, label=label)
    plt.scatter(x[0], y[0], c=color, marker='o', s=0.1)
    # Annotate the end of the line with text
    annotation_text = df[annotation_column].iloc[-1]
    plt.annotate(annotation_text, xy=(x[0], y[0]), xytext=(x[0] - 20, y[0] - 20), fontsize=3, color=color)

colors = ['red']  # Add more colors as needed

for label, (df, color) in zip(data_frames.keys(), zip(data_frames_list, colors)):
    plot_dataframe_with_annotation(df, color=color, linewidth=0.5, label=label, annotation_column='Your_Annotation_Column')
    
# Draw coastlines, countries, and states
m.drawcoastlines(linewidth=0.2, color='#595e63', zorder=3)
m.drawstates(linewidth=0.2, color='#595e63', zorder=3)
m.drawcountries(linewidth=0.2, color='#595e63', zorder=3)
m.drawmapboundary(fill_color='#abdbf2')
m.fillcontinents(color='#ffeabe', lake_color='#a6cae0', zorder=2)  # Land color
m.drawmeridians(np.arange(0, 360, 5), labels=[0, 0, 0, 1], color='gray', linewidth=0.3, fontsize=3, zorder=1)
m.drawparallels(np.arange(0, 90, 5), labels=[1, 0, 0, 0], color='gray', linewidth=0.3, fontsize=3, zorder=1)

# Plot the PAR boundary
lons_par, lats_par = m(par['LON'].values, par['LAT'].values)
m.plot(lons_par, lats_par, color='red', linestyle='dashed', linewidth=0.5, zorder=3)

# Loop through the list of DataFrames and plot each on the Basemap
for label, df in zip(data_frames.keys(), data_frames_list):
    plot_dataframe_with_annotation(df, color='black', linewidth=0.5, label=label, annotation_column='Your_Annotation_Column')

# Save the plot
plt.savefig(f'{folder}/summary_images/{year}BST{quarter}.png', dpi=300, bbox_inches='tight')

transfertoterra = f'{nas_local_dir}/Tropical Cyclone Group/ARTC DRAFTS/{year}/Tracks/Summary of Tracks'

# Transfer the source image to the NAS local directory
transfer_to_nas(f'{folder}/summary_images/{year}BST{quarter}.png', transfertoterra)


