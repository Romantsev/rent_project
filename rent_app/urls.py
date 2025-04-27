from django.urls import path
from . import views

urlpatterns = [
   path('properties/', views.list_properties, name='list_properties'),
   path('property/create/', views.create_property, name='create_property'),
   
   path('owners/', views.list_owners, name='list_owners'),
   path('owner/create/', views.create_owner, name='create_owner'),
   
   path('developers/', views.list_developers, name='list_developers'),
   path('developer/create/', views.create_developer, name='create_developer'),
]
