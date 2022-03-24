from django import forms
class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=128)
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    email = forms.EmailField(max_length=32,required=False)
    password = forms.CharField(max_length=128,widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=128,widget=forms.PasswordInput())


