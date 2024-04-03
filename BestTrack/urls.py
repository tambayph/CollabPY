from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,  name='app-besttrack'),
    path('latest-image/', views.best_track_serve_latest_image, name='best_track_serve_latest_image'),
    path('download_img/<str:file_name>/', views.best_track_download_image, name='best_track_download_image'),
    path('create/<str:datetime_string>', views.create,  name='app-besttrack-create'),
]