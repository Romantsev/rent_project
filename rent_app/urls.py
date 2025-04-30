from django.urls import path
from . import views

urlpatterns = [
   path('properties/', views.list_properties, name='list_properties'),
   path('property/create/', views.create_property, name='create_property'),
   path('property/<int:property_id>/', views.view_property, name='view_property'),
   
   path('owners/', views.list_owners, name='list_owners'),
   path('register/', views.register_user, name='register'),
   path('login/', views.login_user, name='login'),
   path('logout/', views.logout_user, name='logout'),
   
   path('developers/', views.list_developers, name='list_developers'),
   path('developer/create/', views.create_developer, name='create_developer'),
]
