from .models import Credit,CreditService
from django import forms
from django.utils import timezone as tz

class DebtRegistrationForm(forms.ModelForm):
    class Meta:
        model=Credit
        fields =['credit_date','credit_agency','amount','credit_service_date','comment']
        widgets = {
            'credit_agency':forms.TextInput(attrs={'class':'form-control'}),
            'credit_date': forms.TextInput(attrs={'type': 'date','value':tz.now().date(),'class':'form-control'}),
            'credit_service_date': forms.TextInput(attrs={'type': 'date','value':tz.now().date(),'class':'form-control'}),
            'amount':forms.TextInput(attrs={'type':'number','class':'form-control'}),
            'comment':forms.TextInput(attrs={'class':'form-control'}),
            }

class DebtServiceForm(forms.ModelForm):
    def __init__(self,user,*args,**kwargs):
        super(DebtServiceForm,self).__init__(*args,**kwargs)
        self.fields['debt_id'].queryset=Credit.objects.filter(user_id=user,voided=0,paid=0)
    class Meta:
        model= CreditService
        fields = ['debt_id','service_date','amount','comment']
        widgets ={
            'debt_id':forms.Select(attrs={'class':'form-control'}),
            'service_date': forms.TextInput(attrs={'type':'date', 'value':tz.now().date(),'class':'form-control'}),
            'amount':forms.NumberInput(attrs={'class':'form-control'}),
            'comment':forms.TextInput(attrs={'class':'form-control'}),
            }