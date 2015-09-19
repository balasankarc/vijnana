from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import SignInForm
import bcrypt
from .models import User
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    return render(request, 'home.html')


def user_signin(request):
    error = ""
    if request.POST:
        form = SignInForm(request.POST)
        if form.is_valid():
            input_username = form.cleaned_data['username']
            input_password = form.cleaned_data['password']
            print "Username", input_username
            print "Password", input_password
            try:
                user = User.objects.get(username=input_username)
                password = user.password
                if bcrypt.hashpw(input_password, password) == password:
                    print "Success"
                    request.session['user'] = user.username
                    return HttpResponseRedirect('/')
                else:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                error = "Incorrect username or password"
                print "Exception caught"
    else:
        if 'user' in request.session.keys():
            # If user already logged in, redirect to homepage
            return HttpResponseRedirect('/')
    return render(request, 'signin.html', {'error': error})


def user_signout(request):
    if 'user' in request.session.keys():
        del request.session['user']
    return HttpResponseRedirect('/')
