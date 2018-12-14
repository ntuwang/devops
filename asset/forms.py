#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from django import forms
from asset.models import ServerAsset, Clouds, Owners


class CloudsForm(forms.ModelForm):
    class Meta:
        model = Clouds
        fields = ('name', 'region_id', 'provider', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'region_id': forms.TextInput(attrs={'class': 'form-control'}),
            'provider': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OwnerForms(forms.ModelForm):
    class Meta:
        model = Owners
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(OwnerForms, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'


class ServerAssetForm(forms.ModelForm):
    class Meta:
        model = ServerAsset
        fields = ['hostname', "public_ip", "size", "os", "status", "region","owner"]
        widgets = {
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'private_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'public_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'os': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
        }
