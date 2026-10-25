from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('find-donors/', views.find_donors_view, name='find_donors'),
    path('requests/', views.request_list_view, name='request_list'),
    path('requests/<int:pk>/', views.request_detail_view, name='request_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('requests/new/', views.create_request_view, name='create_request'),
    path('requests/<int:pk>/status/', views.update_request_status_view, name='update_request_status'),
]
