import hashlib
import os

from django.db import models


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


class Department(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class User(models.Model):
    username = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    department = models.ForeignKey(Department)


class Subject(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    credit = models.IntegerField()
    course = models.CharField(max_length=10)
    semester = models.CharField(max_length=10)
    department = models.ForeignKey(Department)
    staff = models.ManyToManyField(User, related_name="teachingsubjects")
    students = models.ManyToManyField(User, related_name="subscribedsubjects")


class Resource(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject)
    resourcefile = models.FileField(upload_to=set_filename)
    uploader = models.ForeignKey(User)
