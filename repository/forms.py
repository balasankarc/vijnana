from django import forms


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SignUpForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    fullname = forms.CharField()
    department = forms.CharField()
