def cache(seconds=0, minutes=0, hours=0, days=0, public=True):
    from django.views.decorators.cache import cache_control 
    max_age = seconds + minutes * 60 + hours * 60 * 60 + days * 60 * 60 * 24
    return cache_control(max_age=max_age, public=public)
