from datetime import datetime
import os
import subprocess
import sys
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

#declaring absolute path
folder = os.path.dirname(os.path.abspath(__file__))
isohyet_folder_path = os.path.join(folder, 'isohyet_images')
def serve_latest_image(request):
    try:
        # Get the list of files in the folder
        files = os.listdir(isohyet_folder_path)

        # Filter out non-image files (you may need to adjust this depending on your file types)
        image_files = [file for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        # Sort the image files by modification time (latest first)
        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(isohyet_folder_path, x)), reverse=True)

        # Get the path of the latest image
        latest_image_path = os.path.join(isohyet_folder_path, image_files[0])

        with open(latest_image_path, 'rb') as image_file:
            return HttpResponse(image_file.read(), content_type="image/jpeg")  # Adjust content_type as needed
    except (FileNotFoundError, IndexError):
        return HttpResponse(status=404)

def index(request):
    context = {
        'title': 'Isohyetal',
    }

    img_dir = f'{folder}/isohyet_images/'
    files = [f for f in os.listdir(img_dir) if f.endswith('.png')]

    # Handling search functionality
    query = request.GET.get('q')

    # Check if the query is None or empty string, and if so, display all files
    if query is None or query.strip() == "":
        sorted_files = files  # Show all files if there's no search query
    else:
        # Filtering files based on the query
        filtered_files = [file for file in files if query.lower() in file.lower()]

        if not filtered_files:
           return render(request, 'isohyetal_index.html', {'files': files, 'query': query, 'not_found_message': 'File not Found'})

        # Get the modification time for each file and create a list of tuples (file, modification time)
        files_with_mtime = [(file, os.path.getmtime(os.path.join(img_dir, file))) for file in filtered_files]

        # Sort the files based on modification time (recent first)
        sorted_files = [file[0] for file in sorted(files_with_mtime, key=lambda x: x[1], reverse=True)]

    paginator = Paginator(sorted_files, 10)  # Show 10 files per page

    page = request.GET.get('page')
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)  # Show the first page if page parameter is not an integer
    except EmptyPage:
        files = paginator.page(paginator.num_pages)  # Deliver the last page if page is out of range

    # Get the latest file
    latest_file = sorted_files[0] if sorted_files else None
    context['latest_file'] = os.path.join(img_dir, latest_file) if latest_file else None
    print("Image Path:", os.path.join(img_dir, latest_file))
    return render(request, 'isohyetal_index.html', {'files': files, 'query': query, 'context': context, 'path': img_dir})
    
def create(request, datetime_string):
    # get python directory path
    python_path = sys.executable

    # Define the path to the main.py script
    script_path = os.path.join(os.path.dirname(__file__), 'Isohyetal_v2.py')
    command = [python_path, script_path, datetime_string]

    try:
        subprocess.run(command, check=True, shell=False)
        return HttpResponse('Isohyetal created successfully!', status=200)
    except subprocess.CalledProcessError as e:
        return HttpResponse(f"Error running the script: {e}")

def display_last_image(request):
    img_dir = f'{folder}/isohyet_images/'
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
    img_dir = f'{folder}/isohyet_images/'  # Update this path to the folder where your img files are stored
    file_path = os.path.join(img_dir, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as img_file:
            response = HttpResponse(img_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)
