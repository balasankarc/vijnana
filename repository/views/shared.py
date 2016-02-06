def is_user_hod(request, subject):
    """This method returns whether the current user is hod of the subject."""
    if not request.user.is_authenticated():
        return False
    user = request.user
    if user.profile.status == 'hod' and \
            user.profile.department == subject.department:
        return True
    else:
        return False


def is_user_current_user(request, username):
    if not request.user.is_authenticated():
        return False
    if request.user.username == username:
        return True
    else:
        return False


def is_user_hod_or_teacher(request, subject=None):
    if not request.user.is_authenticated():
        return False
    user = request.user
    if subject:
        if user.profile.department == subject.department:
            if user.profile.status == 'hod' or \
                    user.profile.status == 'teacher':
                return True
            else:
                return False
        else:
            return False
    else:
        if user.profile.status == 'hod' or user.profile.status == 'teacher':
            return True
        else:
            return False
