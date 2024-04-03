# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 11:36:41 2023

@author: WF026
"""
import os
import requests
import csv
import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
from datetime import datetime

from matplotlib.patheffects import withStroke
from adjustText import adjust_text 
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def main():

    script = os.path.dirname(os.path.abspath(__file__))

    date = sys.argv[1]
    category = sys.argv[2]
    tcid = sys.argv[3]
    tcbnumber = sys.argv[4]

    # Parse the date string
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:8])
    time = int(date[8:10])

    # Map time to your specified format
    time_mapping = {
        0: "8:00 AM",
        3: "11:00 AM",
        6: "2:00 PM",
        9: "5:00 PM",
        12: "8:00 PM",
        15: "11:00 PM",
        18: "2:00 AM",
        21: "5:00 AM"
    }

    time_str = time_mapping.get(time, "")

    # Format the datetime object as "11:00 AM, 16 August 2023"
    formatted_date = datetime(year, month, day).strftime("%d %B %Y")

    ############### Download API #####################
    # url = f'http://10.10.1.97/fast/api/highest-signal/?id={year}{tcid}'
    url = f'http://10.10.1.97/fast/api/signal/?iwsid={year}{tcid}&bulletinNum={tcbnumber}'

    response = requests.get(url)

    data = response.json()

    # Extract relevant data from the JSON
    result = data['result'][0]['selection']
    intname = data['result'][0]['int_tc_name']
    tcname = data['result'][0]['tc_name']
    result_data = json.loads(result)

    # Create a new CSV file for each id and write the headers
    with open('signal.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['geocode', 'province', 'municipality', 'signal'])

        # Loop through the data and write each row to the CSV file
        for item in result_data:
            row = [item['geocode'], item['province'], item['municipality'], item['signal']]
            writer.writerow(row)
            
    ############### Merge JSON #####################

    # Load the JSON data
    with open(f'{script}/Resources/Edited_Municipal.json') as f:
        data = json.load(f)

    # Load the CSV data
    with open('signal.csv', encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        # Skip header row if it exists
        header = next(reader, None)
        # Loop over rows and add to JSON data
        for i, row in enumerate(reader):
            # Assuming the first column of the CSV contains ADM2_PCODE values
            adm3_group = row[0]
            # Assuming the second column of the CSV contains frequency values
            Signals = row[3]
            # Find the feature in the JSON data with the matching ADM2_PCODE
            for feature in data['features']:
                if feature['properties']['ADM3_GROUP'] == adm3_group:
                    # Add the frequency value to the properties dictionary of the feature
                    feature['properties']['Signals'] = Signals
                    
            else:
            # If no matching feature was found, set Signals to 0 
                    feature['properties']['Signals'] = 0
                    
    # save updated JSON file
    with open('signal.json', 'w') as f:
        json.dump(data, f)

    ############### Create Chart #####################

    # Read in the GeoJSON file
    gdf = gpd.read_file('signal.json')
    sdf = gpd.read_file(f'{script}/Resources/Edited_Province.json')

    # Define the frequency values and corresponding colors
    color_dict = {'1': '#00CCFF', '2': '#FFFF00', '3': '#FFC000', '4': '#FF0000', '5': '#FF00FF'}

    # Define a function to return the color for each value
    def get_color(value):
        return color_dict.get(str(value), '#73b273')

    # Plot the GeoDataFrame with custom colors
    fig, ax = plt.subplots(figsize=(17, 22), dpi=450)
    gdf.plot(ax=ax, color=[get_color(value) for value in gdf['Signals']])

    # Remove the numbers on the axis
    ax.set_xticks([])
    ax.set_yticks([])

    # Set the face color and edge color
    ax.set_facecolor('#002673')
    # Set the edge color for all sides
    for spine in ax.spines.values():
        spine.set_color('white')


    # Create legend handles and labels
    handles = [mpatches.Patch(color=color_dict[str(i)], label='TCWS #' + ' ' + str(i)) for i in range(5, 0, -1)]
    labels = [h.get_label() for h in handles]

    # Add legend to the plot
    ax.legend(handles=handles, labels=labels, loc='upper left',  prop={'family': 'Arial', 'weight': 'bold', 'size': 18})

    # Show the plot)

    # Set the background color of the legend frame to black
    ax.get_legend().get_frame().set_facecolor('black')

    ax.get_legend().get_title().set_color('white')

    # Set the font color of the legend labels to white
    for text in ax.get_legend().get_texts():
        text.set_color("white")

    # Add sdf as a transparent overlay
    sdf.plot(ax=ax, facecolor='none', edgecolor='black', alpha=1)

    #SET BOUNDARIES
    ###############################################################################    
    # Open the JSON file
    with open('signal.json') as f:
        # Load the JSON data
        data = json.load(f)

    signal_values = [1, 2, 3, 4, 5]  # The desired signal values

    filtered_features = []

    for feature in data['features']:
        signal = feature['properties'].get('Signals')
        if signal is not None and int(signal) in signal_values:
            filtered_features.append(feature)
   
    lowest_lat = float('inf')
    lowest_lon = float('inf')
    highest_lat = float('-inf')
    highest_lon = float('-inf')

    def process_coordinates(coordinates):
        nonlocal lowest_lat, lowest_lon, highest_lat, highest_lon
        
        if isinstance(coordinates[0], list):
            for coord in coordinates:
                process_coordinates(coord)
        else:
            lat = coordinates[1]
            lon = coordinates[0]
            
            if lat < lowest_lat:
                lowest_lat = lat
                
            if lon < lowest_lon:
                lowest_lon = lon
            
            if lat > highest_lat:
                highest_lat = lat
                
            if lon > highest_lon:
                highest_lon = lon

    for feature in filtered_features:
        coordinates = feature['geometry']['coordinates']
        process_coordinates(coordinates)

        ymin = lowest_lat - 1
        xmin = lowest_lon - 0.5
        ymax = highest_lat + 0.5
        xmax = highest_lon + 0.5 

    # Desired aspect ratio
    new_width = 17
    new_height = 22
    aspect_ratio = new_width / new_height

    # Calculate the center of the original rectangle
    xcenter = (xmin + xmax) / 2
    ycenter = (ymin + ymax) / 2

    # Calculate the width and height of the original rectangle
    width = xmax - xmin
    height = ymax - ymin

    # Calculate the aspect ratio of the original rectangle
    original_aspect_ratio = width / height

    if original_aspect_ratio > aspect_ratio:
        # The rectangle is wider than the desired aspect ratio
        # Adjust the height to match the aspect ratio
        new_height = width / aspect_ratio
        # Shift the rectangle to the center
        ymin = ycenter - new_height / 2
        ymax = ycenter + new_height / 2
    else:
        # The rectangle is taller than the desired aspect ratio
        # Adjust the width to match the aspect ratio
        new_width = height * aspect_ratio
        # Shift the rectangle to the center
        xmin = xcenter - new_width / 2
        xmax = xcenter + new_width / 2

    # # set the new limits for the plot
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # ###############################################################################
    # #ADD LABEL
    # ###############################################################################  
    
    provincelabels = pd.read_excel(f'{script}/Resources/Province Labels.xlsx')
    # Initialize a dictionary to store the (lat, lon) coordinates for each unique label
    label_coordinates = {}
    unique_labels = set()

    # Iterate through the rows in the GeoDataFrame (gdf)
    for idx, row in gdf.iterrows():
        label = row["ADM2_EN"]
        signal = row["Signals"]

        # Check if the label has already been plotted or if there is no signal value
        if label in unique_labels or signal is None:
            continue  # Skip this iteration if label already exists or no signal value

        # Find the corresponding coordinates (lat, lon) from the Excel file based on the "Province" column
        matching_row = provincelabels[provincelabels["PROVINCE"] == label]
        
        if not matching_row.empty:
            lat_str = matching_row.iloc[0]["lat"]
            lon_str = matching_row.iloc[0]["lon"]
            
            # Convert latitude and longitude strings to float
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                label_coordinates[label] = (lat, lon)
            except ValueError:
                print(f"Failed to convert coordinates for label: {label}")

        unique_labels.add(label) 

        # Define the white outline effect
        white_outline = withStroke(linewidth=3, foreground="white")

        # Annotate the point with the outlined label
        plt.annotate(label, (lon, lat), color='black', path_effects=[white_outline])
        
    ##############################################################################
    # ADD TXTBOX
    ############################################################################### 
    
    # Add a white rectangle patch at the bottom of the figure
    rect = mpatches.Rectangle((0, 0), 1, 0.08, facecolor='white', transform=ax.transAxes)
    ax.add_patch(rect)

    # Add text on the rectangle patch
    text = 'PAGASA-DOST'
    ax.text(0.83, 0.04, text, color='black', fontsize=20, fontweight='bold', ha='left', va='center', transform=ax.transAxes)

    # Add text on the rectangle patch
    text = f'Tropical Cyclone Bulletin #{tcbnumber} - {category} "{tcname}" {{{intname}}}'

    ax.text(0.7, 0.045, text, color='black', fontsize=19, fontweight='bold', ha='right', va='center', transform=ax.transAxes)

    # Add text on the rectangle patch
    text1 = f'{time_str},{formatted_date}'
    ax.text(0.45, 0.025, text1, color='black', fontsize=20, ha='right', va='center', transform=ax.transAxes)

    # Load the logo image
    logo_img = plt.imread(f'{script}/Resources/PAGASA_Logo.png')  # Replace with the path to your PNG image

    # Calculate the width of the logo in axes coordinates
    logo_width = 0.1 * logo_img.shape[1] / fig.dpi

    # Add pagasa-logo2 PNG image on the most right of the rectangle patch
    logo_box = OffsetImage(logo_img, zoom=0.08)
    logo_ab = AnnotationBbox(logo_box, (1 - logo_width, 0.04), frameon=False,
                            xycoords='axes fraction', boxcoords="axes fraction", pad=0.0)
    ax.add_artist(logo_ab)

    ###############################################################################
    #SAVE
    ###############################################################################    
    # Save the plot as a high-quality figure
    
    savedir = os.path.join(script, f'signal_images/{tcname}_TCB#{tcbnumber}_{year}.jpg')

    fig.savefig(savedir, bbox_inches='tight', format='jpg', dpi=450)

if __name__ == '__main__':
    main()    

