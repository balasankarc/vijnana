from repository.models import User


def current_user(request):
    """This method returns the current user from session value."""
    if 'user' in request.session:
        return User.objects.get(username=request.session['user'])
    else:
        return None


def is_user_hod(request, subject):
    """This method returns whether the current user is hod of the subject."""
    user = current_user(request)
    if user.status == 'hod' and user.department == subject.department:
        return True
    else:
        return False


def is_user_current_user(request, username):
    if request.session['user']:
        if username == request.session['user']:
            return True
        else:
            return False
    else:
        return False
