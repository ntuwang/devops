from django import forms
from sysadmin.models import *


class SaltGroupForm(forms.ModelForm):
    class Meta:
        model = SaltGroup
        fields = ('nickname',)
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SaltFileForm(forms.Form):
    file_path = forms.FileField(label=u'选择文件', )
    remote_path = forms.CharField(label=u'远程路径', widget=forms.TextInput(attrs={'class': 'form-control'}))
    remark = forms.CharField(label=u'备注', widget=forms.TextInput(attrs={'class': 'form-control'}))
