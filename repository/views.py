from django.shortcuts import render_to_response


def home(request):
    content = "This is the homepage"
    return render_to_response('home.html', {'content': content})
