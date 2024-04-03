from datetime import datetime
import sys
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import subprocess
import os
import json


folder = os.path.dirname(os.path.abspath(__file__))
def index(request):
    json_file_path = f'{folder}/data.json'

    # Load JSON data from the file
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Extract values from the JSON data
    tc_id = json_data['result'][0]['iws_id']
    bulletin_number = json_data['result'][0]['bulletin_number']

    # Pass the values to the template
    context = {'tc_id': tc_id, 'bulletin_number': bulletin_number}

    # Retrieve the files in the folder
    image_dir = f'{folder}/signal_images/'
    files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]

    # Handling search functionality
    query = request.GET.get('q')

    # Check if the query is None or an empty string, and if so, display all files
    if query is None or query.strip() == "":
        sorted_files = files  # Show all files if there's no search query
    else:
        # Filtering files based on the query
        filtered_files = [file for file in files if query.lower() in file.lower()]

        if not filtered_files:
            return render(request, 'signal_index.html', {'files': files, 'query': query, 'not_found_message': 'File not Found'})

        # Get the modification time for each file and create a list of tuples (file, modification time)
        files_with_mtime = [(file, os.path.getmtime(os.path.join(image_dir, file))) for file in filtered_files]

        # Sort the files based on modification time (recent first)
        sorted_files = [file[0] for file in sorted(files_with_mtime, key=lambda x: x[1], reverse=True)]

    paginator = Paginator(sorted_files, 10)  # Show 10 files per page

    page = request.GET.get('page')
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)  # Show the first page if the page parameter is not an integer
    except EmptyPage:
        files = paginator.page(paginator.num_pages)  # Deliver the last page if the page is out of range

    # Include the context when rendering the template
    return render(request, 'signal_index.html', {'files': files, 'query': query, **context})


def create(request, datetime_string):
    # get python directory path
    python_path = sys.executable

    # Define the path to the main.py script
    script_path = os.path.join(os.path.dirname(__file__), 'main.py')
    command = [python_path, script_path]


    # Parse the string into a datetime object
    date_format = "%Y%m%d%H%M"  # Year, month, day, hour, minute
    parsed_datetime = datetime.strptime(datetime_string, date_format)

    return HttpResponse(parsed_datetime)

    # try:
    #     subprocess.run(command, check=True, shell=False)
    # except subprocess.CalledProcessError as e:
    #     return HttpResponse(f"Error running the script: {e}")
    # finally:
    #     return HttpResponse('Success')
    
def display_last_image(request):
    img_dir = f'{folder}/signal_images/'
    files = [f for f in os.listdir(img_dir) if f.endswith('.png')]
    if files:
        last_img = max(files, key=lambda x: os.path.getctime(os.path.join(img_dir, x)))
        file_path = os.path.join(img_dir, last_img)
        with open(file_path, 'rb') as img_file:
            response = HttpResponse(img_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{last_img}"'
            return response
    else:
        return HttpResponse("No .img files found in the 'output' directory.")

def display_last_image_page(request):
    return render(request, 'display_last_img.html')


def download_image(request, file_name):
    img_dir = f'{folder}/signal_images/'  # Update this path to the folder where your img files are stored
    file_path = os.path.join(img_dir, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as img_file:
            response = HttpResponse(img_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)
