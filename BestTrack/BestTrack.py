import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from mpl_toolkits.basemap import Basemap
import numpy as np
import math
from math import ceil, floor
from datetime import datetime
import os
import sys

########################################################################################################################
# Input the filename
year = sys.argv[1]
# Assuming tcid is the second command-line argument
if len(sys.argv) > 2:
    tcid = sys.argv[2]
    
    # Ensure tcid has at least two digits
    tcid = tcid.zfill(2)

tcname = sys.argv[3]

# Check if BST is provided
if len(sys.argv) > 4:
    BST = sys.argv[4]
else:
    BST = None

# Input the filename
script = os.path.dirname(os.path.abspath(__file__))
transfer = os.path.join(script, '../copytotera')
sys.path.append(transfer)

from copytotera import mount_network_server, transfer_to_nas, nas_local_dir
nas_remote_path = 'wd.s.dstor.pagasa.local/wfs/Tropical Cyclone/'
# Mount the network server
mount_network_server(nas_remote_path, nas_local_dir)

if BST is not None:
    file = os.path.join(nas_local_dir, f'Tropical Cyclone Best Track Data/PH{year}{BST}/PH{year}{tcid}{BST}.txt')
    transfertoterra = f'{nas_local_dir}/Publication_Preliminary TC Report/{year}/Charts/Tracks/{BST}/'

else:
    file = os.path.join(nas_local_dir, f'Tropical Cyclone Best Track Data/PH{year}/PH{year}{tcid}.txt')
    transfertoterra = f'{nas_local_dir}/Publication_Preliminary TC Report/{year}/Charts/Tracks/'

shapedir = os.path.join(script, 'Resources/Provinces')
pardir = os.path.join(script, 'Resources/PAR.csv')

########################################################################################################################
# Option for map boundaries
# Enter: 1 = manual
#        2 = automatic
# Default automatic(2)
opt_boundaries = 2
manual_lat_min_round = 5
manual_lat_max_round = 45
manual_lon_min_round = 105
manual_lon_max_round = 160
# Note:
# Ratio lat:lon, 4:6
########################################################################################################################
# Manual adjustment of the position of the labels, input positions are in latitude (y_lat) and longitude (x_lon)
# Empty the list if you don't want to do manual adjustment
exclude_date = []
y_lat = []
x_lon = []
########################################################################################################################

plt.rcParams['font.family'] = 'Dejavu Sans'

np.seterr('raise')

# DATA PREPARATION
# Used to prevent error in tokenizing data
names_temp = ['0','1','2','3','4','5','6','7']

# Open the files
par = pd.read_csv(pardir, sep=',')
best = pd.read_csv(file, sep=' ', header=None, skiprows=[0], names=names_temp)
best_head = open(file, 'r')

first_line = best_head.readline()

# Prepare the data
best.drop(['1', '4'], inplace=True, axis=1)
best.columns = ['date', 'lat', 'lon', 'wind', 'pres', 'cat']
best['lat'] = best['lat'].astype(float)
best['lon'] = best['lon'].astype(float)
best['lat'] = best['lat'] * 0.1
best['lon'] = best['lon'] * 0.1

catColor = []
category = []

for row in best['cat']:
    if row == 1: catColor.append('#00ff00'), category.append('Tropical Depression')
    elif row == 2: catColor.append('#ffff00'), category.append('Tropical Storm')
    elif row == 3: catColor.append('#ff9900'), category.append('Severe Tropical Storm')
    elif row == 4: catColor.append('#ff0000'), category.append('Typhoon')
    elif row == 5: catColor.append('#cc00ff'), category.append('Super Typhoon')
    elif row == 6: catColor.append('#a5a5a5'), category.append('Low')
    else: catColor.append('#008080'), category.append('Extratropical')

best['catColor'] = catColor
best['category'] = category

# Change the format
best['date'] = pd.to_datetime(best['date'],format='%y%m%d%H')

# Filter lat and lon at 00 UTC
best_lat_00 = best[pd.DatetimeIndex(best['date']).hour == 0].lat
best_lon_00 = best[pd.DatetimeIndex(best['date']).hour == 0].lon

# Filter lat and lon at 12 UTC
best_lat_12 = best[pd.DatetimeIndex(best['date']).hour == 12].lat
best_lon_12 = best[pd.DatetimeIndex(best['date']).hour == 12].lon

# Filter the dates at 00 UTC
best_date = pd.DatetimeIndex(best[pd.DatetimeIndex(best['date']).hour == 0].date).day

# Format the date with leading zero
best_date = best_date.tolist()
best_date = list(map('{:02d}'.format, best_date))

# Start and end date of TC to be used for the plot title
start_date = best['date'].iloc[0]
start_date = start_date.strftime('%d %b %Y')
start_date = datetime.strptime(start_date, '%d %b %Y')
end_date = best['date'].iloc[-1]
end_date = end_date.strftime('%d %b %Y')
end_date = datetime.strptime(end_date, '%d %b %Y')

if start_date.month == end_date.month:
    title_date = '{} - {}'.format(start_date.strftime('%d'),end_date.strftime('%d %B %Y'))
else:
    title_date = '{} - {}'.format(start_date.strftime('%d %B'), end_date.strftime('%d %B %Y'))

# TITLE OF THE PLOT
# Create a temporary data frame for the cat and category
temp = best[(best['cat']!=6) & (best['cat']!=7)]

# Reset the index   
index = pd.Index(range(len(temp)))  
temp = temp.set_index(index)

# Find the index of the highest category
temp_index = temp['cat'].idxmax()
hi_cat = temp['category'].iloc[temp_index]

localName = first_line[22:37].strip()
intName = first_line[44:59].strip()

if intName == 'UNNAMED':
    title_legend = '{} {} \n {}'.format(hi_cat, localName, title_date)
else:
    title_legend = '{} {} ({}) \n {}'.format(hi_cat, localName, intName, title_date)
########################################################################################################################
# SETTING MAP BOUNDARIES AUTOMATICALLY

# Determine the range of lat and lon
lat_min = best['lat'].min()
lon_min = best['lon'].min()

lat_max = best['lat'].max()
lon_max = best['lon'].max()

# Round down
lat_min_round = 5 * floor(lat_min/5)
lon_min_round = 5 * floor(lon_min/5)

if lat_min_round == 5:
    lat_min_round = 3
if 18 < lat_min_round < 26:
    lat_min_round = 15

# Check the difference from the rounded lat_min to the lat_min
# This is done to give enough space between the point and the edge of the chart
check_lat_min_diff = abs(lat_min - lat_min_round)
check_lon_min_diff = abs(lon_min - lon_min_round)

if check_lat_min_diff < 1.0:
    lat_min_round = lat_min_round - 5
if check_lon_min_diff < 1.0:
    lon_min_round = lon_min_round - 5

# Round up
lat_max_round = 5 * ceil(lat_max/5)
lon_max_round = 5 * ceil(lon_max/5)

if lat_max_round == 25:
    lat_max_round = 28

if 116 < lon_min_round < 136:
    lon_min_round = 116

# Check the difference
check_lat_max_diff = abs(lat_max - lat_max_round)
check_lon_max_diff = abs(lon_max - lon_max_round)

if check_lat_max_diff < 1.0:
    lat_max_round = lat_max_round + 5
if check_lon_max_diff < 1.0:
    lon_max_round = lon_max_round + 5

if 116 < lon_max_round < 127:
    lon_max_round = 128

# Find difference between the range of lat and lon
diff_lat = abs(lat_max_round-lat_min_round)
diff_lon = abs(lon_max_round-lon_min_round)

# Check the ratio between lat/lon
ratio = diff_lat/diff_lon

if ratio == 1.0:
    lon_min_round = lon_min_round - 5
    lat_min_round = lat_min_round - 5
    if lat_min_round == 5:
        lat_min_round = 3
    diff_lat = abs(lat_max_round - lat_min_round)
    diff_lon = abs(lon_max_round - lon_min_round)

if diff_lon > diff_lat:
    diff_lat = diff_lon * (4/6)
    new_lat_max = lat_min_round + diff_lat

    # Adjust the graph more on the south
    if abs(lat_max_round - new_lat_max) >= 10:
        lat_min_round = lat_min_round - 5
        if lat_min_round == 5:
            lat_min_round = 3
        else:
            lat_min_round = 0
        new_lat_max = lat_min_round + diff_lat

    # Adjust the new_lat_max if it is smaller compared to the lat_max_round
    while lat_max_round >= new_lat_max:

        lon_min_round = lon_min_round - 5

        if 116 < lon_min_round < 136:
            lon_min_round = 116

        if lon_max_round == 135:
            lon_max_round = 140

        if lon_min_round == 115.0:
            lon_min_round = 113.0

        diff_lon = abs(lon_max_round-lon_min_round)
        diff_lat = diff_lon * (4 / 6)
        new_lat_max = lat_min_round + diff_lat

    lat_max_round = new_lat_max

else:
    diff_lon = diff_lat * (6/4)
    lon_max_round = lon_min_round + diff_lon

    if lon_max_round == 135:
        lon_max_round == 138
        lon_min_round = lon_max_round - diff_lon
    if lon_min_round == 115.0:
        lon_min_round = 113.0
        lon_max_round = lon_min_round + diff_lon
#######################################################################################################################
# PLOT

fig, ax = plt.subplots(figsize=(11,8.333))

# Option for manual or automatic input of map boundaries
if opt_boundaries == 1:
    lat_min_round = manual_lat_min_round
    lat_max_round = manual_lat_max_round
    lon_min_round = manual_lon_min_round
    lon_max_round = manual_lon_max_round
else:
    lat_min_round = lat_min_round
    lat_max_round = lat_max_round
    lon_min_round = lon_min_round
    lon_max_round = lon_max_round

m = Basemap(llcrnrlat=lat_min_round, urcrnrlat=lat_max_round,
            llcrnrlon=lon_min_round, urcrnrlon=lon_max_round, resolution='h')
m.readshapefile(shapedir,'Provinces',
                linewidth=0.2, color='#343A40', zorder=3)

# Draw boundaries
m.drawcoastlines(linewidth=0.2, color='#595e63', zorder=3)
m.drawstates(linewidth=0.2, color='#595e63', zorder=3)
m.drawcountries(linewidth=0.2, color='#595e63', zorder=3)
m.drawmapboundary(fill_color='#abdbf2')
m.fillcontinents(color='#ffeabe', zorder=2)

# Lat, Lon label
m.drawmeridians(np.arange(0,360,5),labels=[0,0,0,1],color='gray',linewidth=0.3,fontsize=7, zorder= 1)
m.drawparallels(np.arange(0,90,5),labels=[1,0,0,0],color='gray',linewidth=0.3, fontsize =7, zorder = 1)

# Plot the line track
lons = best['lon']
lats = best['lat']

points = np.array(m(lons,lats)).T

# Plot the line track
i=-1
for start, stop in zip(points[:-1], points[1:]):
    i = i+1
    x, y = zip(start, stop)
    ax.plot(x, y, color=best['catColor'].iloc[i], linewidth= 2.5, alpha=1, zorder=3)


# Extrapolate points used for the arrow head
lat1 = best['lat'].iloc[-2]
lat2 = best['lat'].iloc[-1]

lon1 = best['lon'].iloc[-2]
lon2 = best['lon'].iloc[-1]

ang1 = math.atan2((lat2-lat1),(lon2-lon1))
lon_end = lon2 + math.cos(ang1) * 0.5
lat_end = lat2 + math.sin(ang1) * 0.5

x_len = lon_end - best['lon'].iloc[-1]
y_len = lat_end - best['lat'].iloc[-1]

new_row = {'date':best['date'].iloc[-1], 'lat': lat_end, 'lon': lon_end,
           'cat': best['cat'].iloc[-1], 'catColor': best['catColor'].iloc[-1],
           'category': best['category'].iloc[-1]}

# Plot the arrow head
ax.arrow(best['lon'].iloc[-1], best['lat'].iloc[-1],x_len,y_len,head_width = 0.1,
         head_length = 0.1, overhang=0.2, linewidth = 2.5, width = 0.001, color = best['catColor'].iloc[-1], zorder=3)

# Plot the PAR boundary
# lons_par,lats_par = m(par['LON'],par['LAT'])
# ax.plot(lons_par,lats_par,color='black', linestyle= 'dashed', linewidth=0.7, zorder=2)

lons_par, lats_par = m(par['LON'].to_numpy(), par['LAT'].to_numpy())
ax.plot(lons_par, lats_par, color='black', linestyle='dashed', linewidth=0.7, zorder=2)

# Plot the 00 UTC points
lons_00, lats_00 = m(best_lon_00,best_lat_00)
ax.scatter(lons_00, lats_00, marker='o', color='black', s=15, zorder=4)

# Plot the 12 UTC points
lons_12, lats_12 = m(best_lon_12,best_lat_12)
ax.scatter(lons_12, lats_12, marker= 'o', color='white', edgecolor='black',s=20, linewidth=0.5, zorder=4)
########################################################################################################################
# ANNOTATE THE DATE

# For manual adjustments of the date labels
n = len(exclude_date)

print('Dates Excluded:')

if n == 0:
    print('None')

while n != 0:
    for i in range(len(exclude_date)):

        # Find the index of the date to be excluded in the best_date list
        str_exclude_date = str(exclude_date[i]).zfill(2)
        index_exclude_date = best_date.index(str(str_exclude_date))

        # Find the index of the date to be excluded in the best_la/lon_00
        index_exclude_temp = best.index[pd.DatetimeIndex(best['date']).day == exclude_date[i]].tolist()
        index_exclude = index_exclude_temp[0]

        best_date_ex= best_date[index_exclude_date]
        best_lat_ex = best_lat_00[index_exclude]
        best_lon_ex = best_lon_00[index_exclude]

        # Delete the row
        del best_date[index_exclude_date]
        best_lon_00 = best_lon_00.drop([index_exclude])
        best_lat_00 = best_lat_00.drop([index_exclude])

        print(best_date_ex, best_lat_ex, best_lon_ex)

        ax.annotate(best_date_ex,(best_lon_ex,best_lat_ex),xytext=(x_lon[i],y_lat[i]),
                    fontsize=7, fontname='Dejavu Sans', zorder=4)

        n -= 1

# Automatic positioning of date labels

print('Dates:')

px2 = []
py2 = []
d = 0.4

date_00_index = best_lon_00.index.tolist()

for i in range(len(date_00_index)):
    try:
        # check
        line_x = best['lon'].iloc[date_00_index[i]]
        line_y = best['lat'].iloc[date_00_index[i]]

        if date_00_index[i] == 0:
            line1_x = line_x
            line1_y = line_y

            line2_x = best['lon'].iloc[date_00_index[i] + 1]
            line2_y = best['lat'].iloc[date_00_index[i] + 1]

        elif date_00_index[i] == (best.shape[0]-1):
            line1_x = best['lon'].iloc[date_00_index[i] - 1]
            line1_y = best['lat'].iloc[date_00_index[i] - 1]

            line2_x = line_x
            line2_y = line_y

        else:
            line1_x = best['lon'].iloc[date_00_index[i] - 1]
            line1_y = best['lat'].iloc[date_00_index[i] - 1]

            line2_x = best['lon'].iloc[date_00_index[i] + 1]
            line2_y = best['lat'].iloc[date_00_index[i] + 1]

        x2 = line2_x - line_x
        y2 = line2_y - line_y

        angle = math.atan2(y2,x2)

    except FloatingPointError:
        angle = 0

    deg = math.degrees(angle)


    if x2 == 0 and y2 == 0:
        x = line_x + 0.4
        y = line_y
    elif x2 > 0 and y2 == 0:
        x = line_x
        y = line_y + 0.4
    elif x2 > 0 and y2 > 0:
        x = line_x + (d * math.cos(angle - math.radians(90)))
        y = line_y + (d * math.sin(angle - math.radians(90))) - 0.1
    else:
        x = line_x + (d * math.cos(angle - math.radians(90)))
        y = line_y + (d * math.sin(angle - math.radians(90)))

    px2.append(x)
    py2.append(y)

# Annotate the date
for i, (x,y) in enumerate(zip(px2,py2)):
    ant = ax.annotate(best_date[i],(x,y),fontsize=7, fontname='Dejavu Sans', zorder=4)
    print(best_date[i],y,x)
########################################################################################################################
# CUSTOMIZE THE LEGEND

legend_elements= [Line2D([0], [0], color='#cc00ff', lw=4, label='Super Typhoon'),
                    Line2D([0], [0], color='#ff0000', lw=4, label='Typhoon'),
                    Line2D([0], [0], color='#ff9900', lw=4, label='Severe Tropical Storm'),
                    Line2D([0], [0], color='#ffff00', lw=4, label='Tropical Storm'),
                    Line2D([0], [0], color='#00ff00', lw=4, label='Tropical Depression'),
                    Line2D([0], [0], color='#a5a5a5', lw=4, label='Low'),
                    Line2D([0], [0], color='#008080', lw=4, label='Extratropical'),
                    Line2D([0], [0], marker='o', lw=0, color='black', label='0000 UTC Position',
                           markerfacecolor='black',  markersize=6),
                    Line2D([0], [0], marker='o', color='white', label='1200 UTC Position',
                           markeredgecolor='black', markersize=6, linewidth=0.5)]


# Temporary variable holder
# This is done to determine the extent of the box in each holder
l = ax.legend(handles=legend_elements,fontsize= 7.5,
            edgecolor='black', facecolor='white',framealpha=1.0, borderpad= 1, loc = 1)

t = ax.text(135,15 , title_legend, fontsize = 12, ha = 'center')

# Position the title and legend
ylimit = ax.get_ylim()
xlimit = ax.get_xlim()

# Find the corresponding lon of the maximum lat
temp_lon = best['lon'].iloc[best['lat'].idxmax()]

# Check the distance to determine where the legend should be placed
left = math.dist([temp_lon], [xlimit[0]])
right = math.dist([temp_lon], [xlimit[1]])
top = math.dist([lat_max], [ylimit[1]])

r = fig.canvas.get_renderer()
bb = t.get_window_extent(renderer=r)
ll = l.get_window_extent(renderer=r)

bbox_text = ax.transData.inverted().transform(bb)
bbox_ll = ax.transData.inverted().transform(ll)

width = bbox_text[1,0] - bbox_text[0,0]
height = bbox_text[1,1] - bbox_text[0,1]

w_ll = bbox_ll[1,0] - bbox_ll[0,0]
h_ll = bbox_ll[1,1] - bbox_ll[0,1]

if top<8 and left>right:
    xpos = xlimit[0] + width / 2 + 0.3
    ypos = ylimit[1] - height - 0.2

else:
    xpos = xlimit[1] - width / 2 - 0.3
    ypos = ylimit[1] - height - 0.2

xpos_ll = ((xpos - (w_ll/2)) - xlimit[0]) / (xlimit[1]-xlimit[0])
ypos_ll = ((ypos-(height + h_ll)) - ylimit[0]) / (ylimit[1]-ylimit[0])

ax.text(xpos,ypos, title_legend, fontsize = 12, ha = 'center', weight = 'bold')

ax.legend(handles=legend_elements,fontsize= 7.5,
          edgecolor='black', facecolor='white',framealpha=1.0, borderpad= 1, loc =(xpos_ll,ypos_ll))

Artist.remove(t)
########################################################################################################################
# SAVE THE FILE

savedir = os.path.join(script, f'best_track_images/{localName}.png')

plt.savefig(savedir, bbox_inches='tight', pad_inches=0.1, dpi=300)

# Transfer the source image to the NAS local directory
transfer_to_nas(f'{script}/best_track_images/{localName}.png', transfertoterra)

plt.show()
