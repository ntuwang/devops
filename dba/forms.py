from django import forms
from .models import *


class DBInfoForm(forms.ModelForm):
    class Meta:
        model = DBInfo
        fields = '__all__'
        widgets = {
            'db_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'db_ip': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'db_port': forms.TextInput(attrs={'type':'number','class': 'form-control', 'required': 'required'}),
            'status': forms.Select(attrs={'type':'number','class': 'form-control', 'required': 'required'}),
            'comment': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),

        }
