from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,  name='app-isohyetal'),
    path('create/<str:datetime_string>', views.create,  name='app-isohyetal-create'),
    path('display_last_img/', views.display_last_image_page, name='display_last_image_page'),
    path('download_last_img/', views.display_last_image, name='download_last_image'),
    path('download_img/<str:file_name>/', views.download_image, name='download_image'),
    path('latest-image/', views.serve_latest_image, name='serve_latest_image'),
]
