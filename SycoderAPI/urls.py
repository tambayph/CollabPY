# pyright: reportGeneralTypeIssues=false
from django.urls import path


from . import views

urlpatterns = [
    path('station', views.PagasaStnList.as_view(), name='station'),
    path('synop', views.SynopticDataList.as_view(), name='synop'),
    # path('rainfall', views.RainfallDataList.as_view(), name='rainfall'),
]
