from django import forms
from .models import Projects,Deploys


class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'jenkins_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'target_path': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'deploy_path': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'remote_history_dir': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'before_deploy': forms.TextInput(attrs={'class': 'form-control'}),
            'after_deploy': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DeploysForm(forms.ModelForm):
    class Meta:
        model = Deploys
        fields = ('project','version','pkg_name','host')
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'version': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'pkg_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'host': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }
