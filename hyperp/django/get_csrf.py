def get_csrf(request):
    from django.middleware.csrf import get_token
    return f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">'
