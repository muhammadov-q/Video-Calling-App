from django.urls import path
from .views import *


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('confirm-email/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('password_reset/', password_reset, name='password_reset'),
    path('reset/<str:uidb64>/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
]
