from django.urls import path
from django.contrib.auth import views as auth_views
from users import views
from users.views import (
    login_signup_view,
    signup_view,
    dashboard,
    profile_section,  # Changed from profile_view
    update_profile,
    upload_status,
    delete_status
)

urlpatterns = [
    # Authentication
    path('', login_signup_view, name='login_signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('user-status/<str:username>/', views.user_status_modal, name='user_status_modal'),
    
    # Profile
    path('profile/', profile_section, name='profile_view'),  # Changed to profile_section
    path('profile/edit/', update_profile, name='edit_profile'),
    
    # Status
    path('upload-status/', upload_status, name='upload_status'),
    path('delete-status/<int:status_id>/', delete_status, name='delete_status'),
    path('update-profile-bio/', views.update_profile_bio, name='update_profile_bio'),
    
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/profile/', profile_section, name='profile'),  # Changed to profile_section
    path('dashboard/status/', views.status_section, name='status'),  # Changed to status_section
    path('generate-bio/', views.generate_bio, name='generate_bio'),
]