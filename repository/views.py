import os

import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.images import get_image_dimensions
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from PIL import Image

from .forms import (AssignOrRemoveStaffForm, NewResourceForm, NewSubjectForm,
                    ProfilePictureCropForm, ProfilePictureUploadForm,
                    SearchForm, SignInForm, SignUpForm)
from .models import Department, Profile, Resource, Subject, User

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
    if 'user' in request.session:
        return User.objects.get(username=request.session['user'])
    else:
        return None


def is_user_hod(request, subject):
    user = current_user(request)
    if user.status == 'hod' and user.department == subject.department:
        return True
    else:
        return False


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
            input_password = form.cleaned_data['password'].encode('utf-8')
            try:
                user = User.objects.get(username=input_username)
                username = user.username
                password = user.password.encode('utf-8')
                if bcrypt.hashpw(input_password, password) == password:
                    request.session['user'] = username
                    request.session['usertype'] = user.status
                    return HttpResponseRedirect('/')
                else:
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                error = "Incorrect username or password"
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
                input_password = form.cleaned_data['password'].encode('utf-8')
                input_name = form.cleaned_data['fullname']
                input_department = form.cleaned_data['department']
                password_hash = bcrypt.hashpw(input_password, bcrypt.gensalt())
                user = User(username=input_username,
                            password=password_hash,
                            name=input_name,
                            department_id=input_department)
                user.save()
                request.session['user'] = input_username
                request.session['usertype'] = user.status
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
                return HttpResponseRedirect('/resource/'+str(resource.id))
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
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
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
                query = form.cleaned_data['query']
                resource_list = Resource.objects.filter(title__contains=query)
                if resource_list:
                    return render(request, 'search.html',
                                  {
                                    'resource_list': resource_list,
                                    'query': query
                                  })
                else:
                    raise ObjectDoesNotExist
        except ObjectDoesNotExist:
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
    if subject_list:
        return render(request, 'my_subjects.html',
                      {
                        'subject_list': subject_list,
                      })
    else:
        return render(request, 'error.html',
                      {
                        'error': 'You are not subscribed to any subjects'
                      }, status=404)


def view_subject(request, subject_id):
    try:
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
                is_hod = is_user_hod(request, subject)
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
    except ObjectDoesNotExist:
        return render(request, 'error.html',
                      {
                        'error': 'The subject you requested does not exist.'
                      }, status=404)


def subscribe_me(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        subject.students.add(current_user(request))
        subject.save()
        return HttpResponseRedirect('/subject/'+subject_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html',
                      {
                        'error': 'The subject you requested does not exist.'
                      }, status=404)


def unsubscribe_me(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        if 'user' in request.session:
            user = current_user(request)
            if user in subject.students.all():
                subject.students.remove(user)
                subject.save()
        return HttpResponseRedirect('/subject/'+subject_id)
    except ObjectDoesNotExist:
        return render(request, 'error.html',
                      {
                        'error': 'The subject you requested does not exist.'
                      }, status=404)


def assign_staff(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    is_hod = is_user_hod(request, subject)
    if request.POST and is_hod:
        try:
            form = AssignOrRemoveStaffForm(request.POST)
            if form.is_valid():
                for staff_id in form.cleaned_data['staffselect']:
                    staff = User.objects.get(id=staff_id)
                    subject.staff.add(staff)
        except Exception, e:
            print e
    else:
        staff_list = {}
        for department in Department.objects.all():
            staff_list[department.name] = [x for x in department.user_set.all()
                                           if x.status == 'teacher' or
                                           x.status == 'hod']
        return render(request, 'assign_staff.html',
                      {
                        'is_hod': is_hod,
                        'staff_list': staff_list,
                        'subject': subject
                      })
    return HttpResponseRedirect('/subject/'+subject_id)


def remove_staff(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    if 'user' in request.session:
        user = current_user(request)
        if user.status == 'hod' and user.department == subject.department:
            is_hod = True
    if request.POST:
        print "POST"
        try:
            form = AssignOrRemoveStaffForm(request.POST)
            if form.is_valid():
                for staff_id in form.cleaned_data['staffselect']:
                    staff = User.objects.get(id=staff_id)
                    subject.staff.remove(staff)
                    subject.save()
        except Exception, e:
            print e
    else:
        staff_list = subject.staff.all()
        print staff_list
        return render(request, 'remove_staff.html',
                      {
                        'is_hod': is_hod,
                        'staff_list': staff_list,
                        'subject': subject
                      })
    return HttpResponseRedirect('/subject/'+subject_id)


def new_subject(request):
    department_list = Department.objects.all()
    error = ''
    if request.POST:
        try:
            form = NewSubjectForm(request.POST)
            if form.is_valid():
                input_code = form.cleaned_data['code']
                input_name = form.cleaned_data['name']
                input_credit = form.cleaned_data['credit']
                input_course = form.cleaned_data['course']
                input_semester = form.cleaned_data['semester']
                input_department = current_user(request).department.id
                subject = Subject(code=input_code, name=input_name,
                                  credit=input_credit, course=input_course,
                                  semester=input_semester,
                                  department_id=input_department)
                subject.save()
                return HttpResponseRedirect('/subject/'+str(subject.id))
        except IntegrityError:
            error = 'Subject Code already exists'
    return render(request, 'new_subject.html',
                  {'department_list': department_list,
                   'error': error
                   })


def upload_profilepicture(request, username):
    user = User.objects.get(username=username)
    if not user:
        return render(request, 'error.html',
                      {
                        'error': 'The user you requested does not exist.'
                      }, status=404)
    elif user != current_user(request):
        return render(request, 'error.html',
                      {
                        'error': 'You are not permitted to do this.'
                      }, status=404)
    else:
        try:
            p = user.profile
        except:
            p = Profile(user_id=user.id)
            p.save()
        if request.POST:
            print "Post"
            print p.user.username
            form = ProfilePictureUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    image = request.FILES['image']
                    w, h = get_image_dimensions(image)
                    if w < 200 or h < 200 or w > 1000 or h > 1000:
                        error = "Image dimension should be between 500x500 and 1000x1000"
                        raise
                    if p.picture:
                        os.remove(p.picture.path)
                    p.picture = image
                    p.save()
                    print p.picture.path
                    return HttpResponseRedirect('/user/'+user.username+'/crop_profilepicture')
                except:
                    return render(request, 'uploadprofilepicture.html',
                                  {'user': user, 'error': error})
            else:
                return render(request, 'uploadprofilepicture.html',
                              {'user': user})
        else:
            return render(request, 'uploadprofilepicture.html', {'user': user})
        return HttpResponseRedirect('/user/' + user.username)


def crop_profilepicture(request, username):
    user = User.objects.get(username=username)
    if not user:
        return render(request, 'error.html',
                      {
                        'error': 'The user you requested does not exist.'
                      }, status=404)
    elif user != current_user(request):
        return render(request, 'error.html',
                      {
                        'error': 'You are not permitted to do this.'
                      }, status=404)
    else:
        user = User.objects.get(username=username)
        if request.POST:
            if user.profile.picture:
                form = ProfilePictureCropForm(request.POST)
                if form.is_valid():
                    x1 = int(float(form.cleaned_data['x1']))
                    y1 = int(float(form.cleaned_data['y1']))
                    x2 = int(float(form.cleaned_data['x2']))
                    y2 = int(float(form.cleaned_data['y2']))
                    image = Image.open(user.profile.picture.path)
                    cropped_image = image.crop((x1, y1, x2, y2))
                    cropped_image.save(user.profile.picture.path)
                    return HttpResponseRedirect('/user/'+user.username)
                else:
                    print "Failure"
                    print form
            else:
                return HttpResponseRedirect('/user/'+user.username)
        else:
            return render(request, 'cropprofilepicture.html', {'user': user})


def profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'profile.html', {'user': user})
