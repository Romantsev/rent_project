from django.urls import path
from . import views

urlpatterns = [
    path('properties/', views.list_properties, name='list_properties'),
    path('property/create/', views.create_property, name='create_property'),
]
