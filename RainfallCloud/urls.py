from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,  name='app-rainfall-cloud'),
    path('rainfallcloud/', views.index1,  name='app-rainfall-cloud_v2'),
    path('map-discussion/', views.index_map_discussion,  name='app-map-discussion'),
    path('create-map-discussion/<str:datetime_string>/', views.create_map_discussion, name='app-map-discussion-create'),
    path('create/<str:datetime_string>/', views.create, name='app-rainfall-cloud-create'),
    path('createnoimage/<str:datetime_string>/', views.createnoimage, name='app-rainfall-cloud-create-noimage'),
    path('display_last_pptx/', views.display_last_pptx_page, name='display_last_pptx_page'),
    path('download_last_pptx/', views.display_last_pptx, name='download_last_pptx'),
    path('download_last_pptx_map/', views.display_last_pptx_map, name='download_last_pptx_map'),
    path('download_pptx/<str:file_name>/', views.download_pptx, name='download_pptx'),
    path('download_pptx_map/<str:file_name>/', views.download_pptx_map, name='download_pptx_map'),
    path('delete_file/', views.delete_file, name='delete_file'),

]
