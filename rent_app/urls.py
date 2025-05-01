from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
   path('', lambda request: redirect('properties/', permanent=True)),
   
   path('properties/', views.list_properties, name='list_properties'),
   path('property/create/', views.create_property, name='create_property'),
   path('property/<int:property_id>/', views.view_property, name='view_property'),
   path('property/<int:property_id>/edit/', views.edit_property, name='edit_property'),
   path('property/<int:property_id>/delete/', views.delete_property, name='delete_property'),
   path('clear_properties/', views.clear_properties, name='clear_properties'),

   path('export_json/', views.export_json, name='export_json'),
   path('import_json/', views.import_json, name='import_json'),

   path('owners/', views.list_owners, name='list_owners'),
   path('register/', views.register_user, name='register'),
   path('login/', views.login_user, name='login'),
   path('logout/', views.logout_user, name='logout'),
   path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
   path('profile/<int:user_id>/edit/', views.edit_profile, name='edit_profile'),
   path('profile/<int:user_id>/delete/', views.delete_profile, name='delete_profile'),
   
   path('developer/<int:developer_id>/', views.view_developer, name='view_developer'),
   path('developers/', views.list_developers, name='list_developers'),
   path('developer/create/', views.create_developer, name='create_developer'),
   path('developer/<int:developer_id>/edit/', views.edit_developer, name='edit_developer'),
   path('developer/<int:developer_id>/delete/', views.delete_developer, name='delete_developer'),
   path('clear_developers/', views.clear_developers, name='clear_developers'),

   path('property/<int:property_id>/inspection/add/', views.add_inspection, name='add_inspection'),
   path('inspection/<int:inspection_id>/edit/', views.edit_inspection, name='edit_inspection'),
   path('inspection/<int:inspection_id>/delete/', views.delete_inspection, name='delete_inspection'),
]
