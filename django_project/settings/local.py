from .base import *

DEBUG = True
SECRET_KEY = 'fn2HTM6IO6DEuigh63ishgPQ0jg)n1+_n7y=h_pqas6Kalg%)xd%0t5a=*kdng1!48_5dhg#_'
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
