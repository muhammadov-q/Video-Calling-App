from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('confirm-email/<str:uidb64>/<str:token>/', views.confirm_email, name='confirm_email'),
]
