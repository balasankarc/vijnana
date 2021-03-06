import hashlib
import os

from django.db import models
from django.contrib.auth.models import User


def set_questionpapername(instance, filename):
    hashout = hashlib.md5()
    filenamesplit = os.path.splitext(filename)
    input_filename = filenamesplit[0].replace(
        ' ', '_').replace(',', '_').replace('.', '_')
    extension = filenamesplit[1]
    hashout.update(input_filename)
    if len(input_filename) < 10:
        outfilename = input_filename + hashout.hexdigest() + extension
    else:
        outfilename = input_filename[:10] + '_' + \
            hashout.hexdigest() + input_filename[-10:] + extension
    return os.path.join('questionpapers', outfilename)


def set_filename(instance, filename):
    '''Set a unique file name to the uploaded resource before saving it'''
    hashout = hashlib.md5()
    filenamesplit = os.path.splitext(filename)
    input_filename = filenamesplit[0].replace(
        ' ', '_').replace(',', '_').replace('.', '_')
    extension = filenamesplit[1]
    hashout.update(input_filename)
    if len(input_filename) < 10:
        outfilename = input_filename + hashout.hexdigest() + extension
    else:
        outfilename = input_filename[:10] + '_' + \
            hashout.hexdigest() + input_filename[-10:] + extension
    return os.path.join('resources', outfilename)


def set_profilepicturename(instance, filename):
    filenamesplit = os.path.splitext(filename)
    extension = filenamesplit[1]
    name = instance.user.username + extension
    return os.path.join('profile_pictures', name)


class Department(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User)
    department = models.ForeignKey(Department)
    status = models.CharField(max_length=15)
    address = models.TextField()
    picture = models.ImageField(upload_to=set_profilepicturename, blank=True)
    bloodgroup = models.CharField(max_length=5)
    phone = models.CharField(max_length=15)

    def __unicode__(self):
        return "Profile of " + self.user.username


class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    credit = models.CharField(max_length=5)
    course = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    department = models.ForeignKey(Department)
    staff = models.ManyToManyField(User, related_name="teachingsubjects")
    students = models.ManyToManyField(User, related_name="subscribedsubjects")
    description = models.TextField(max_length=5000)

    def __unicode__(self):
        return self.name


class Resource(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject)
    resourcefile = models.FileField(upload_to=set_filename)
    uploader = models.ForeignKey(User)

    def __unicode__(self):
        return self.title


class Exam(models.Model):
    name = models.CharField(max_length=100)
    totalmarks = models.CharField(max_length=10)
    time = models.CharField(max_length=10)
    subject = models.ForeignKey(Subject)
    questionpaper = models.FileField(upload_to=set_questionpapername)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Question(models.Model):
    text = models.CharField(max_length=5000, unique=True)
    module = models.IntegerField()
    part = models.CharField(max_length=10)
    co = models.CharField(max_length=10)
    level = models.CharField(max_length=10)
    exam = models.ManyToManyField(Exam)
    subject = models.ForeignKey(Subject)

    def __unicode__(self):
        return self.text
