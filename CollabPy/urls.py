"""
URL configuration for CollabPy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include

import logging
from django.conf import settings
from django.conf.urls.static import static

from .views import index, contact

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
    # path('api-auth/', include('rest_framework.urls'))

    path('', index, name='index'),
    path('contact/', contact, name='contact'),

    path('signal/', include('SignalCreator.urls')),
    path('isohyetal/', include('Isohyetal.urls')),
    path('isothermal/', include('Isothermal.urls')),
    path('rainfall-cloud/', include('RainfallCloud.urls')),
    path('besttrack/', include('BestTrack.urls')),
    path('gsmap/', include('GSMap.urls')),
    path('gsmapsynop/', include('GSMapSynop.urls')),
    path('api/v2/', include('SycoderAPI.urls')),

    path('dashboard/', include('Dashboard.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)


logger = logging.getLogger('django')

# Add this middleware to log the request/response data
class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        logger.info(
            f'{request.method} {request.path} - {response.status_code}')
        return response
