from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,  name='app-signal'),
    # path('create/', views.create,  name='app-signal-create'),
    path('create/<str:datetime_string>', views.create,  name='app-signal-create'),
     path('display_last_img/', views.display_last_image_page, name='display_last_image_page'),
    path('download_last_img/', views.display_last_image, name='download_last_image_signal'),
    path('download_img/<str:file_name>/', views.download_image, name='download_image_signal'),
   
]
