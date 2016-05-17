from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^create_department', create_department),
    url(r'^delete_department', delete_department),
    url(r'^update_department', update_department),
]
