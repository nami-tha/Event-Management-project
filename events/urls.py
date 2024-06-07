from django.urls import path
from .views import (UserListView,
    EventListView,
    EventDetailView,
    RegistrationCreateView,
    UserDetailView,
    UserCreateView,
    EventRegistrationCountView,
    LoginView,
    LogoutView,
)


urlpatterns = [
    path('events/', EventListView.as_view(), name='event-list'),
    path('event/<int:id>', EventDetailView.as_view(), name='event-detail'),
    path('user/create/', UserCreateView.as_view(), name='user-create'),
    path('users/list/', UserListView.as_view(), name='user-list'),
    path('user/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('event/register/', RegistrationCreateView.as_view(), name='event-register'),
    path('event/count/', EventRegistrationCountView.as_view(), name='event-register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    
]
