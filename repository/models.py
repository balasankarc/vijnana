from django.db import models


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


class Resource(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject)
    resourcefile = models.FileField(upload_to='resources')
