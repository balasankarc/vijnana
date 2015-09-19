from django import forms


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
