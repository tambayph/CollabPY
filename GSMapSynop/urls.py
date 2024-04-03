from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,  name='app-gsmapsynop'),
    path('latest-image/', views.gsmapsynop_serve_latest_image, name='gsmapsynop_serve_latest_image'),
    path('download_img/<str:file_name>/', views.gsmapsynop_download_image, name='gsmapsynop_download_image'),
  
]