from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import SignInForm
import bcrypt
from .models import User
from django.core.exceptions import ObjectDoesNotExist


def home(request):
    content = "This is the homepage"
    return render(request, 'home.html', {'content': content})


def user_signin(request):
    error = ""
    print "reached here"
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
    print "reached here"
    return render(request, 'signin.html', {'error': error})
