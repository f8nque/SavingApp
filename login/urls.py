from django.urls import path
from . import views
urlpatterns =[
    path('login/',views.LoginView.as_view(),name="login"),
    path('password_reset',views.PasswordResetView.as_view(),name="password_reset"),
    path('register/',views.RegistrationView.as_view(),name='registration'),
    path('logout/',views.LogoutView.as_view(),name="logout"),
]