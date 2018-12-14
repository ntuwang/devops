#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from django import forms
from user.models import *


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                             'placeholder': '用户名',
                                                                             'required': 'required'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': '密 码', 'required': 'required'}))
    error_messages = {
        'invalid_login': ("Please enter a correct %(username)s and password. "
                          "Note that both fields may be case-sensitive."),
        'inactive': ("This account is inactive."),
    }


class UserForm(forms.ModelForm):
    class Meta:
        model = Users
        email = forms.CharField(label='邮箱')
        fields = ('username', 'email', 'mobile', 'role', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名', 'required': 'required',
                                               'data-validate-length-range': '5,30'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
            'qq': forms.TextInput(attrs={'class': 'form-control', 'data-validate-length-range': '4,16'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'data-validate-length': '11'}),
            'role': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'is_active': forms.CheckboxInput(attrs={'style': 'padding-top:5px;'})
        }
