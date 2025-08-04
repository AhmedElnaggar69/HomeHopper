# booking/urls.py
print("DEBUG: urls.py - START LOADING")
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # For logout

# This print statement will show what 'views.ApartmentCreateView' is *at the moment urls.py is loaded*
# If it's a function here, that's the problem.
print(f"DEBUG: urls.py - After views import. Type of views.ApartmentCreateView: {type(views.ApartmentCreateView)}")

urlpatterns = [
    # Starter Page
    path('', views.starter_view, name='starter'),

    # User Authentication
    path('login/', views.user_login_view, name='login_url'),
    path('signup/', views.user_signup_view, name='signin_url'),
    path('logout/', views.user_logout_view, name='logout_url'),

    # Owner Authentication
    path('owner/login/', views.owner_login_view, name='login_url_owner'),
    path('owner/signup/', views.owner_signup_view, name='signin_url_owner'),

    # User Dashboard & Apartment Search
    path('user/dashboard/', views.index_user_view, name='index_user'),
    path('apartments/', views.apartment_list_view, name='apartment_list'),

    # Owner Dashboard & Listing Management
    path('owner/dashboard/', views.owner_dashboard_view, name='owner_dashboard'),
    # Uncommented the problematic lines for debugging
    path('owner/apartments/add/', views.ApartmentCreateView.as_view(), name='add_apartment'),
    path('owner/apartments/<int:pk>/edit/', views.ApartmentUpdateView.as_view(), name='edit_apartment'),
    path('owner/apartments/<int:pk>/delete/', views.ApartmentDeleteView.as_view(), name='delete_apartment'),

    # Profile Management
    path('profile/user/', views.user_profile_view, name='user_profile'),
    path('profile/owner/', views.owner_profile_view, name='owner_profile'),

    # Chat Functionality
    path('chats/', views.chat_list_view, name='chat_list'),
    path('chats/<int:participant_id>/', views.chat_detail_view, name='chat_detail'),
    path('apartments/<int:apartment_id>/chat/', views.initiate_chat_from_apartment, name='initiate_chat_from_apartment'),
]
print("DEBUG: urls.py - END LOADING")
