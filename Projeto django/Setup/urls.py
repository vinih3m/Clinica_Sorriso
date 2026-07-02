from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from Clinica_Sorriso.views import CustomLoginView, redirect_pos_login

def home(request):
    return redirect('login')

urlpatterns = [
    path('', home, name='home'),

    path('admin/', admin.site.urls),

    # LOGIN / LOGOUT
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # REDIRECIONAMENTO
    path('pos-login/', redirect_pos_login, name='redirect_pos_login'),

    # 🔥 TODAS AS ROTAS DO SISTEMA VÊM DO APP
    path('', include('Clinica_Sorriso.urls')),
]
