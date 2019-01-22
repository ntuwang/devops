from django import forms
from .models import *


class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'app_type': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'jenkins_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'dest_path': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'packlist': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'local_dir': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'remote_history_dir': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'before_deploy': forms.TextInput(attrs={'class': 'form-control'}),
            'after_deploy': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DeploysForm(forms.ModelForm):
    class Meta:
        model = Deploys
        fields = ('project', 'branch', 'jenkinsbd','host')
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'jenkinsbd': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'branch': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'host': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }
