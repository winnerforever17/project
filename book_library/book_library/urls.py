from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from library import views as library_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login'), name='logout'),
    path('register/', library_views.register, name='register'),
]
