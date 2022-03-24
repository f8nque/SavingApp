from django.shortcuts import render,redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User,UserManager
from django.views import View
from .forms import RegistrationForm
# Create your views here.
class LoginView(auth_views.LoginView):
    template_name = "login/login_form.html"
    redirect_url = "index/"

    #redirect_field_name="next" :default
    #authentication_form =AuthenticationForm (username,password)

class RegistrationView(View):
    non_field_errors ="Passwords do not match!!!"
    def get(self,request,*args,**kwargs):
        form = RegistrationForm()
        return render(request,"login/registration_form.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name =form.cleaned_data['last_name']
            email =form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password =form.cleaned_data['confirm_password']
            check_user = User.objects.filter(username=username)
            if(password != confirm_password):
                return render(request,"login/registration_form.html",{"form":form,'non_field_errors':self.non_field_errors})
            elif(len(check_user) != 0 ):
                return render(request, "login/registration_form.html",
                              {"form": form, 'non_field_errors': "Username already exists"})
            else:
                user = User()
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.email =email
                user.set_password(password)
                user.save()
                return redirect("login")
        else:
            return render(request, "login/registration_form.html", {"form": form})
class LogoutView(auth_views.LogoutView):
    next_page ="/accounts/login"
class PasswordResetView(auth_views.PasswordResetView):
    template_name = "login/password_reset.html"

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    pass