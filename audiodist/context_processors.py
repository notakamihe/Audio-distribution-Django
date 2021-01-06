def is_logged_in (request):
    return { 'is_logged_in': request.user.is_authenticated }