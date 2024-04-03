import pysftp
import gzip
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Path, PathPatch
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import ListedColormap
import os
import sys
from datetime import datetime, timedelta

########################################################################################################################
script = os.path.dirname(os.path.abspath(__file__))
shapedir = os.path.join(script, 'Resources/Provinces')

transfer = os.path.join(script, '../copytotera')
sys.path.append(transfer)

from copytotera import mount_network_server, transfer_to_nas, nas_local_dir

# Define the base remote path
nas_remote_path = 'wd.s.dstor.pagasa.local/wfs/GSMAP'

# Mount the network server
mount_network_server(nas_remote_path, nas_local_dir)

previous_day_date = datetime.now() - timedelta(days=1)
previous_day_formatted = previous_day_date.strftime("%Y/%m/%d")
save_name = previous_day_date.strftime("%Y%m%d")

# SFTP connection details
hostname = 'hokusai.eorc.jaxa.jp'
username = 'rainmap'
password = 'Niskur+1404'  # You may use key-based authentication instead of a password

# Define the SFTP connection options
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking (not recommended for production)

# Establish the SFTP connection
with pysftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts) as sftp:
    # List files in the remote directory
    sftp_path = f'/realtime_ver/v7/hourly_G/{previous_day_formatted}'

    # Change remote directory
    sftp.chdir(sftp_path)

    # List files in the remote directory
    remote_files = sftp.listdir()

    # Specify local directory where you want to download the files
    local_directory = f'{script}/data/{previous_day_formatted}'

    if not os.path.exists(local_directory):
        os.makedirs(local_directory)
    # Download each file in the remote directory to the local directory
    for file_name in remote_files:
        remote_file_path = f'{sftp_path}/{file_name}'
        local_file_path = f'{local_directory}/{file_name}'
        sftp.get(remote_file_path, local_file_path)

    print("Files downloaded successfully.")

# Path of the directory
# sftp_path = f'C:\Users\WF026\Desktop\Summary BST\Test'
    
########################################################################################################################
# Store the files in a list
files = []

for (root,dirs,file) in os.walk(local_directory):
    for f in file:
        if '.gz' in f:
            files.append(os.path.join(root, f))

accu_rr = np.zeros(4320000)

for i, file in enumerate(files):
    gz = gzip.GzipFile(file, 'rb')
    rr = np.frombuffer(gz.read(), dtype=np.float32)
    rr = np.where(rr == -999.9, 0, rr)
    accu_rr = accu_rr + rr

rainfall = accu_rr.reshape((1200, 3600))

########################################################################################################################
## PLOT

rainfall=accu_rr.reshape((1200, 3600))
longitude=np.linspace(0.05, 359.95, 3600)
latitude=np.linspace(59.95, -59.95, 1200)
xmesh_model, ymesh_model = np.meshgrid(longitude, latitude, sparse=False)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,12))

m = Basemap(llcrnrlat=4.5,urcrnrlat=24,llcrnrlon=113,urcrnrlon=128,lat_ts=20,resolution='h')
m.readshapefile(shapedir,'Provinces')

#Draw boundaries
m.drawcoastlines(linewidth=0.6)
m.drawstates(linewidth=0.6)
m.drawcountries(linewidth=0.6)

#Convert to basemap projection scale
lon_map, lat_map = m(xmesh_model, ymesh_model)

# color scheme of the rainfall data
rgb = [[255,255,255],[186,184,184],[0,197,255],[107,251,144],[255,255,0],[255,170,0],[255,0,0],[255,115,223],[132,0,168]]
rgb=np.array(rgb)/255.
cmap = ListedColormap(rgb,"")
boundaries = [0, 10, 25, 50, 100, 200, 300, 500, 5000]
norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, clip=True)

# Plot the rainfall on the basemap
cs = ax.pcolormesh(lon_map,lat_map,rainfall, cmap=cmap, norm=norm)

# Add colorbar
cbar = plt.colorbar(cs, ax=ax, orientation='horizontal', ticks=[0, 10, 25, 50, 100, 200, 300, 500, 5000], pad=0.01, fraction=0.01, aspect=70)
cbar.set_label('mm', size=10)
cbar.ax.set_xticklabels([' ', '10', '25', '50', '100', '200', '300', '500', ' '], fontsize=10)


#######################################################################################################################
# Mask the ocean

#Getting the limits of the map:
x0,x1 = ax.get_xlim()
y0,y1 = ax.get_ylim()
map_edges = np.array([[x0,y0],[x1,y0],[x1,y1],[x0,y1]])

#Getting all polygons used to draw the coastlines of the map
polys = [p.boundary for p in m.landpolygons]

#Combining with map edges
polys = [map_edges]+polys[:]

#Creating a PathPatch
codes = [
    [Path.MOVETO] + [Path.LINETO for p in p[1:]]
    for p in polys
]
polys_lin = [v for p in polys for v in p]
codes_lin = [c for cs in codes for c in cs]
path = Path(polys_lin, codes_lin)
patch = PathPatch(path,facecolor='white', lw=0)

#Masking the data:
ax.add_patch(patch)

########################################################################################################################

#Save the figure
fig.tight_layout()
plt.savefig(f'{script}/gsmap_images/{save_name}.png',bbox_inches='tight', pad_inches=0.1, dpi=600)
plt.show()

previous_day_formatted_dir = previous_day_date.strftime("%Y/%m")

# Transfer the source image to the NAS local directory
transfer_to_nas(f'{script}/gsmap_images/{save_name}.png', f'{nas_local_dir}/{previous_day_formatted_dir}/')

directory_path = f'{script}/data'

# Get a list of all files in the directory
file_list = os.listdir(directory_path)

# Iterate through the files and delete them
for file_name in file_list:
    file_path = os.path.join(directory_path, file_name)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")