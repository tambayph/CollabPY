from datetime import datetime
import os
import subprocess
import sys
from django.http import HttpResponse
from django.shortcuts import render
from pptx import Presentation
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from pathlib import Path
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
#declaring absolute path


folder = os.path.dirname(os.path.abspath(__file__))

def get_absolute_image_path(image_filename):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct the absolute path to the isohyet_images folder
    images_path = os.path.join(BASE_DIR, 'Isohyetal', 'isohyet_images')

    # Construct the absolute path to the image (assuming `image_filename` is a variable holding the image file name)
    image_path = os.path.join(images_path, image_filename)

    return image_path


def index1(request):
    context = {
        'title': 'Rainfall-Cloud',
    }

    pptx_dir = f'{folder}/powerpoints/'
    files = [f for f in os.listdir(pptx_dir) if f.endswith('.pptx')]

    # Handling search functionality
    query = request.GET.get('q')

    # Check if the query is None or empty string, and if so, display all files
    if query is None or query.strip() == "":
        sorted_files = files  # Show all files if there's no search query
    else:
        # Filtering files based on the query
        filtered_files = [file for file in files if query.lower() in file.lower()]

        if not filtered_files:
           return render(request, 'rainfall_cloud_table_index_v2.html', {'files': files, 'query': query, 'not_found_message': 'File not Found'})

        # Get the modification time for each file and create a list of tuples (file, modification time)
        files_with_mtime = [(file, os.path.getmtime(os.path.join(pptx_dir, file))) for file in filtered_files]

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
    context['latest_file'] = os.path.join(pptx_dir, latest_file) if latest_file else None
    print("Image Path:", os.path.join(pptx_dir, latest_file))
    return render(request, 'rainfall_cloud_table_index_v2.html', {'files': files, 'query': query, 'context': context, 'path': pptx_dir})
    
def index(request):
    context = {
    'title': 'Rainfall-Cloud',
    }

    pptx_dir = f'{folder}/powerpoints/'
    files = [f for f in os.listdir(pptx_dir) if f.endswith('.pptx')]

    # Handling search functionality
    query = request.GET.get('q')

    # Check if the query is None or empty string, and if so, display all files
    if query is None or query.strip() == "":
        sorted_files = files  # Show all files if there's no search query
    else:
        # Filtering files based on the query
        filtered_files = [file for file in files if query.lower() in file.lower()]

        if not filtered_files:
           return render(request, 'rainfall_cloud_table_index.html', {'files': files, 'query': query, 'not_found_message': 'File not Found'})

        # Get the modification time for each file and create a list of tuples (file, modification time)
        files_with_mtime = [(file, os.path.getmtime(os.path.join(pptx_dir, file))) for file in filtered_files]

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
    context['latest_file'] = os.path.join(pptx_dir, latest_file) if latest_file else None
    print("Image Path:", os.path.join(pptx_dir, latest_file))
    return render(request, 'rainfall_cloud_table_index.html', {'files': files, 'query': query, 'context': context, 'path': pptx_dir})



def create_map_discussion(request, datetime_string):
    
    # get python directory path
    python_path = sys.executable

    # Define the path to the main.py script
    script_path = os.path.join(os.path.dirname(__file__), 'Map_Discussion.py')
    command = [python_path, script_path, datetime_string]

    try:
            subprocess.run(command, check=True, shell=False)
            success_message = "Script executed successfully"
            response = f"{success_message}"
            return HttpResponse(response, status=200)
    except Exception as e:
        error_message = f"Error running the script: {e}"
        response = HttpResponse(error_message, status=500)
        return response

def create(request, datetime_string):

    # get python directory path
    python_path = sys.executable

    # Define the path to the main.py script
    script_path = os.path.join(os.path.dirname(__file__), 'Rainfall_Cloud.py')
    command = [python_path, script_path, datetime_string]

    try:
            subprocess.run(command, check=True, shell=False)
            success_message = "Script executed successfully"
            response = f"{success_message}"
            return HttpResponse(response, status=200)
    except Exception as e:
        error_message = f"Error running the script: {e}"
        response = HttpResponse(error_message, status=500)
        return response

def createnoimage(request, datetime_string):

    # get python directory path
    python_path = sys.executable

    # Define the path to the main.py script
    script_path = os.path.join(os.path.dirname(__file__), 'RainfallCloud_noimage.py')
    command = [python_path, script_path, datetime_string]

    try:
            subprocess.run(command, check=True, shell=False)
            success_message = "Script executed successfully"
            response = f"{success_message}"
            return HttpResponse(response, status=200)
    except Exception as e:
        error_message = f"Error running the script: {e}"
        response = HttpResponse(error_message, status=500)
        return response


def delete_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')

        # Construct the file path based on your file storage structure
        file_path = f'{folder}/powerpoints/{file_id}'

        # Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)

            # Return a success message as JSON
            return JsonResponse({'status': 'success', 'message': f'File with ID {file_id} deleted successfully.'})
        else:
            # Return an error message as JSON if the file doesn't exist
            return JsonResponse({'status': 'error', 'message': f'File with ID {file_id} does not exist.'})
    else:
        # Handle cases where the view is accessed via GET or other methods
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def display_last_pptx(request):
    pptx_dir = (f'{folder}/powerpoints/') 
    files = [f for f in os.listdir(pptx_dir) if f.endswith('.pptx')]
    if files:
        last_pptx = max(files, key=lambda x: os.path.getctime(os.path.join(pptx_dir, x)))
        file_path = os.path.join(pptx_dir, last_pptx)
        with open(file_path, 'rb') as pptx_file:
            response = HttpResponse(pptx_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{last_pptx}"'
            return response
    else:
        return HttpResponse("No .pptx files found in the 'output' directory.")


def display_last_pptx_map(request):
    pptx_dir = (f'{folder}/powerpoints/') 
    files = [f for f in os.listdir(pptx_dir) if f.endswith('.pptx')]
    if files:
        last_pptx = max(files, key=lambda x: os.path.getctime(os.path.join(pptx_dir, x)))
        file_path = os.path.join(pptx_dir, last_pptx)
        with open(file_path, 'rb') as pptx_file:
            response = HttpResponse(pptx_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{last_pptx}"'
            return response
    else:
        return HttpResponse("No .pptx files found in the 'output' directory.")


def display_last_pptx_page(request):
    return render(request, 'display_last_pptx.html')

def download_pptx(request, file_name):
    pptx_dir = (f'{folder}/powerpoints/')  # Update this path to the folder where your PPTX files are stored
    file_path = os.path.join(pptx_dir, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as pptx_file:
            response = HttpResponse(pptx_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)

def download_pptx_map(request, file_name):
    pptx_dir = (f'{folder}/powerpoints/')  # Update this path to the folder where your PPTX files are stored
    file_path = os.path.join(pptx_dir, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as pptx_file:
            response = HttpResponse(pptx_file.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
    else:
        return HttpResponse("File not found", status=404)



def index_map_discussion(request):
    context = {
        'title': 'Map Discussion',

    }
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date = yesterday.strftime("%m/%d/%Y")
    context['yesterday_date'] = yesterday_date

    pptx_dir = f'{folder}/powerpoints/'
    files = [f for f in os.listdir(pptx_dir) if f.endswith('.pptx')]

    # Handling search functionality
    query = request.GET.get('q')

    # Check if the query is None or empty string, and if so, display all files
    if query is None or query.strip() == "":
        sorted_files = files  # Show all files if there's no search query
    else: 
        # Filtering files based on the query
        filtered_files = [file for file in files if query.lower() in file.lower()]
        
        if not filtered_files:
           return render(request, 'rainfall_cloud_table_index.html', {'files': files, 'query': query, 'not_found_message': 'File not Found'})

        # Get the modification time for each file and create a list of tuples (file, modification time)
        files_with_mtime = [(file, os.path.getmtime(os.path.join(pptx_dir, file))) for file in filtered_files]

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
   
    return render(request, 'map_discussion.html', {'files': files, 'query': query})
