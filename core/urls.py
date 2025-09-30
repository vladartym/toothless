from django.urls import path
from . import views, api

urlpatterns = [
    path('', views.home, name='home'),
    path('api/get/<path:action>/', api.get_data, name='api_get'),
    path('api/post/', api.post_data, name='api_post'),
]
