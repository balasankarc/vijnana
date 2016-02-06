from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from repository.forms import NewResourceForm, SearchForm
from repository.models import Resource, Subject, User


class NewResource(View):
    """Let's a new resource to be created"""

    RESOURCE_TYPES = {
        'Presentation': 'presentation',
        'Paper Publication': 'paper_publication',
        'Subject Note': 'subject_note',
        'Project Thesis': 'project_thesis',
        'Seminar Report': 'seminar_report',
        'Previous Question Paper': 'previous_question_paper'
    }
    subject_list = Subject.objects.all()
    error = ""
    template = "newresource.html"

    def get(self, request):
        user = request.user.is_authenticated()
        if user:
            return render(request, self.template,
                          {
                              'subject_list': self.subject_list,
                              'type_list': self.RESOURCE_TYPES
                          })
        else:
            return render(request, "error.html",
                          {
                              'error': 'You need to be logged in.'
                          }, status=404)

    def post(self, request):
        user = request.user.is_authenticated()
        if user:
            form = NewResourceForm(request.POST, request.FILES)
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
                except Exception as e:
                    self.error = e
                    return render(request, self.template,
                                  {
                                      'error': self.error,
                                      'subject_list': self.subject_list,
                                      'type_list': self.RESOURCE_TYPES
                                  })
            return HttpResponseRedirect('/resource/' + str(resource.id))
        else:
            return render(request, "error.html",
                          {
                              'error': 'You need to be logged in.'
                          }, status=404)


class GetResource(View):
    """Displays details of a resource"""

    def get(self, request, resource_id):
        try:
            resource = Resource.objects.get(id=resource_id)
            return render(request, 'resource.html', {'resource': resource})
        except ObjectDoesNotExist:
            return render(request, 'error.html',
                          {
                              'error': 'The requested resource not found.'
                          }, status=404)


class GetResourcesOfType(View):
    """Displays resources of a specified type"""

    RESOURCE_TYPES = {
        'Presentation': 'presentation',
        'Paper Publication': 'paper_publication',
        'Subject Note': 'subject_note',
        'Project Thesis': 'project_thesis',
        'Seminar Report': 'seminar_report',
        'Previous Question Paper': 'previous_question_paper'
    }

    def get(self, request, type_name):
        try:
            type_name = type_name.replace('_', ' ')
            cat = self.RESOURCE_TYPES[type_name]
            resources = Resource.objects.filter(category=cat)
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
                              'error': 'No resources found.'
                          }, status=404)


class SearchResource(View):
    """Search for resources having a specific query in their title"""
    template = 'search.html'
    error = ''
    status = ''

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        try:
            form = SearchForm(request.POST)
            if form.is_valid():
                query = form.cleaned_data['query']
                resource_list = Resource.objects.filter(
                    title__contains=query)
                if resource_list:
                    return render(request, 'search.html',
                                  {
                                      'resource_list': resource_list,
                                      'query': query
                                  })
                else:
                    raise ObjectDoesNotExist
            else:
                self.error = 'Something went wrong.'
                self.status = 500
        except ObjectDoesNotExist:
            self.error = 'Search returned no results.'
            self.status = 404
        return render(request, 'error.html',
                      {
                          'error': self.error
                      }, status=self.status)
