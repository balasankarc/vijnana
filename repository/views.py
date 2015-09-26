import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import NewResourceForm, SignInForm, SignUpForm, SearchForm
from .models import Department, Resource, Subject, User

RESOURCE_TYPES = {
        'Presentation': 'presentation',
        'Paper Publication': 'paper_publication',
        'Subject Note': 'subject_note',
        'Project Thesis': 'project_thesis',
        'Seminar Report': 'seminar_report',
        'Previous Question Paper': 'previous_question_paper'
        }

USER_STATUS = ['student', 'faculty', 'labstaff', 'administrator', 'hod']


def current_user(request):
    return User.objects.get(username=request.session['user'])


def home(request):
    """Displays home page"""
    return render(request, 'home.html')


def user_signin(request):
    """Handles user's sign in action"""
    error = ""
    username = ""
    if request.POST:
        form = SignInForm(request.POST)
        if form.is_valid():
            input_username = form.cleaned_data['username']
            input_password = form.cleaned_data['password']
            print "Username", input_username
            print "Password", input_password
            try:
                user = User.objects.get(username=input_username)
                username = user.username
                password = user.password
                if bcrypt.hashpw(input_password, password) == password:
                    print "Success"
                    request.session['user'] = username
                    request.session['usertype'] = user.status
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
    return render(request, 'signin.html',
                  {'error': error, 'username': username})


def user_signout(request):
    """Handles user's sign out action"""
    if 'user' in request.session.keys():
        del request.session['user']
        del request.session['usertype']
    return HttpResponseRedirect('/')


def user_signup(request):
    """Handles user's sign up action"""
    department_list = Department.objects.all()
    error = ""
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                input_username = form.cleaned_data['username']
                input_password = form.cleaned_data['password']
                input_name = form.cleaned_data['fullname']
                input_department = form.cleaned_data['department']
                password_hash = bcrypt.hashpw(input_password, bcrypt.gensalt())
                user = User(username=input_username,
                            password=password_hash,
                            name=input_name,
                            department_id=input_department)
                user.save()
                request.session['user'] = input_username
                return HttpResponseRedirect('/')
            except IntegrityError:
                error = error + "Username already in use"
    else:
        if 'user' in request.session.keys():
            # If user already logged in, redirect to homepage
            return HttpResponseRedirect('/')
    return render(request, 'signup.html',
                  {'error': error, 'department_list': department_list})


def new_resource(request):
    """Add a new resource"""
    subject_list = Subject.objects.all()
    error = ""
    if request.POST:
        print request.POST
        form = NewResourceForm(request.POST, request.FILES)
        print form
        if form.is_valid():
            try:
                input_title = form.cleaned_data['title']
                input_category = form.cleaned_data['category']
                input_subject = Subject.objects.get(
                        id=form.cleaned_data['subject'])
                resource_uploader = User.objects.get(
                        username=request.session['user'])
                input_file = request.FILES['resourcefile']
                resource = Resource(
                        title=input_title, category=input_category,
                        subject=input_subject, resourcefile=input_file,
                        uploader=resource_uploader)
                resource.save()
                return HttpResponseRedirect('/')
            except Exception, e:
                error = e
                print error
    return render(request, 'newresource.html',
                  {
                    'error': error,
                    'subject_list': subject_list,
                    'type_list': RESOURCE_TYPES
                  })


def get_resource(request, resource_id):
    """Get details about a single resource"""
    try:
        resource = Resource.objects.get(id=resource_id)
        return render(request, 'resource.html', {'resource': resource})
    except ObjectDoesNotExist:
        return render(request, 'error.html',
                      {
                        'error': 'The requested resource not found.'
                      }, status=404)
    except:
        return render(request, 'error.html',
                      {
                        'error': """Server encountered some error.
                                 Contact Administrator."""
                      }, status=500)


def type_resource_list(request, type_name):
    """Get all resources of a specific type"""
    try:
        type_name = type_name.replace('_', ' ')
        resources = Resource.objects.filter(category=RESOURCE_TYPES[type_name])
        if resources:
            return render(request, 'type_resource_list.html',
                          {
                            'resource_list': resources,
                            'type': type_name
                          })
        else:
            raise
    except:
        return render(request, 'error.html',
                      {
                        'error': 'No resources under the requested category'
                      }, status=404)


def search(request):
    """Search for resources having a specific query in their title"""
    if request.POST:
        try:
            form = SearchForm(request.POST)
            if form.is_valid():
                print dir(form)
                query = form.cleaned_data['query']
                resource_list = Resource.objects.filter(title__contains=query)
                if resource_list:
                    return render(request, 'search.html',
                                  {
                                    'resource_list': resource_list,
                                    'query': query
                                  })
                else:
                    raise
            else:
                raise
        except Exception, e:
            print e
            return render(request, 'error.html',
                          {
                            'error': 'Searched returned no resources.'
                          }, status=404)
    else:
        return render(request, 'search.html')


def my_subjects(request):
    user = current_user(request)
    if user.status == 'teacher':
        subject_list = user.teachingsubjects.all()
    else:
        subject_list = user.subscribedsubjects.all()
    print subject_list
    return render(request, 'my_subjects.html',
                  {
                    'subject_list': subject_list
                  })


def view_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    resource_list = subject.resource_set.all()
    subscription_status = True
    is_hod = False
    has_staff = False
    is_staff = False
    subject_staff_list = subject.staff.all()
    if subject_staff_list:
        has_staff = True
    if 'user' in request.session:
        user = current_user(request)
        if subject not in user.subscribedsubjects.all():
            subscription_status = False
        if user.status == 'hod' and user.department == subject.department:
            is_hod = True
        if user in subject.staff.all():
            is_staff = True
    return render(request, 'subject_resource_list.html',
                  {
                    'subject': subject,
                    'resource_list': resource_list,
                    'subscription_status': subscription_status,
                    'is_hod': is_hod,
                    'is_staff': is_staff,
                    'has_staff': has_staff,
                    'subject_staff_list': subject_staff_list
                  })


def subscribe_me(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    subject.students.add(current_user(request))
    subject.save()
    return HttpResponseRedirect('/subject/'+subject_id)


def unsubscribe_me(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    if 'user' in request.session:
        user = current_user(request)
        if user in subject.students.all():
            subject.students.remove(user)
            subject.save()
    return HttpResponseRedirect('/subject/'+subject_id)
